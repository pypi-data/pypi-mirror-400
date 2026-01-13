import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from scipy.special import ndtri  # for deterministic ggaussian beam
import ctypes
import os
import platform

_ENGINES = {"GPU": None, "CPU": None} # Cache loaded libraries so we don't reload them every frame

GLASS_DB = {
    'BK7':   {'B1': 1.03961212, 'B2': 0.231792344, 'B3': 1.01046945, 'C1': 0.00600069867, 'C2': 0.0200179144, 'C3': 103.560653},
    'F2':    {'B1': 1.39757037, 'B2': 0.159201403, 'B3': 1.26865430, 'C1': 0.00995906143, 'C2': 0.0546931752, 'C3': 119.248346},
    'SF10':  {'B1': 1.62153902, 'B2': 0.256287842, 'B3': 1.64447552, 'C1': 0.0122241457, 'C2': 0.0595736775, 'C3': 147.468793},
    'SiO2':  {'B1': 0.696166300, 'B2': 0.407942600, 'B3': 0.897479400, 'C1': 0.00467914826, 'C2': 0.0135120631, 'C3': 97.9340025}
}

# ==========================================
# Core Ray Class
# ==========================================

class Ray:
    def __init__(self, pos, direction, wavelength, color):
        """
        pos: np.array([x, y])
        direction: np.array([dx, dy]) (will be normalized)
        wavelength: float (nm)
        color: str (for plotting)
        """
        self.pos = np.array(pos, dtype=float)
        
        # Normalize direction vector
        norm = np.linalg.norm(direction)
        if norm == 0:
            raise ValueError("Ray direction cannot be zero vector")
        self.dir = np.array(direction, dtype=float) / norm
        
        self.wavelength = wavelength
        self.color = color
        
        # History of interactions: [(label, pos_vector)]
        self.path = []
        self.terminated = False
        self.detected = False

    def package(self):
        return np.array([-1, 1, self.wavelength, self.pos[0], self.pos[1], self.dir[0], self.dir[1]])

# ==========================================
# Utilities and Functions
# ==========================================

def _get_engine(prefer_gpu):
    global _ENGINES
    
    # Get the file paths for the CUDA and C++ files (Very important for the __init__ file to be in the same folder as the .so/.dll files)
    package_dir = os.path.dirname(os.path.abspath(__file__))
    ext = ".dll" if platform.system() == "Windows" else ".so"
    gpu_path = os.path.join(package_dir, "bin", f"engine_cuda{ext}")
    cpu_path = os.path.join(package_dir, "bin", f"engine_cpp{ext}")

    # Define the Init helper Function (Sets up args for a new lib)
    def init_lib(lib_obj):
        lib_obj.simulate_c.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)
        ]
        lib_obj.simulate_c.restype = None
        return lib_obj

    # Try Loading GPU
    if prefer_gpu:
        if _ENGINES["GPU"]: return _ENGINES["GPU"] # Return cached
        try:
            if os.path.exists(gpu_path):
                print(f"--- INITIALIZING GPU ENGINE ({gpu_path}) ---")
                lib = ctypes.CDLL(gpu_path)
                _ENGINES["GPU"] = init_lib(lib)
                return _ENGINES["GPU"]
            else:
                print(f"Warning: GPU library not found at {gpu_path}")
                print("Falling back to CPU.")
        except Exception as e:
            print(f"Warning: GPU Init Failed ({e}). Falling back to CPU.")

    # Fallback/Default to CPU
    if _ENGINES["CPU"]: return _ENGINES["CPU"] # Return cached
    
    print(f"--- INITIALIZING CPU ENGINE ({cpu_path}) ---")
    
    if not os.path.exists(cpu_path):

        # Critical Error: If CPU engine is missing, the package is broken.
        raise FileNotFoundError(f"CPU Library not found at {cpu_path}. Did you run 'pip install .'? "
                                f"Ensure engine_cpp{ext} exists in the package folder.")
                                
    lib = ctypes.CDLL(cpu_path)
    _ENGINES["CPU"] = init_lib(lib)
    return _ENGINES["CPU"]

def generate_point_source(wavelengths, source_pos, target_element_centre, target_element_aperture, num_rays=5):
    rays = []
    
    # Target geometry
    target_element_centre = np.array(target_element_centre)
    source_pos = np.array(source_pos)
    vec_to_target = target_element_centre - source_pos
    dist = np.linalg.norm(vec_to_target)
    base_angle = np.arctan2(vec_to_target[1], vec_to_target[0])
    
    # Angular spread to hit aperture
    half_angle = np.arctan((target_element_aperture * 0.45) / dist) # 0.45 to stay inside
    angles = np.linspace(base_angle - half_angle, base_angle + half_angle, num_rays)
    
    for lam, color in wavelengths:
        for ang in angles:
            d = np.array([np.cos(ang), np.sin(ang)])
            rays.append(Ray(source_pos, d, lam, color))
    return rays

def generate_parallel_beam(wavelengths, source_pos, target_element_centre, target_element_aperture, num_rays=5):
    """
    Generates a parallel beam of rays (like a laser) that targets a specific element.
    Rays start side-by-side and travel in the same direction.
    """
    rays = []
    
    # Calculate the main propagation direction
    source_pos = np.array(source_pos)
    vec_to_target = np.array(target_element_centre) - source_pos
    dist = np.linalg.norm(vec_to_target)
    direction = vec_to_target / dist
    tangent = np.array([-direction[1], direction[0]])
    
    # We span 90% of the aperture width centered on the axis
    width = target_element_aperture * 0.9
    offsets = np.linspace(-width/2, width/2, num_rays)
    
    for lam, color in wavelengths:
        for offset in offsets:
            start_pos = source_pos + (tangent * offset) # Shift starting position along the tangent            
            rays.append(Ray(start_pos, direction, lam, color)) # Create Ray (Direction is identical for all)
            
    return rays

def generate_gaussian_beam_mc(wavelengths, source_pos, target_element_centre, waist_radius, num_rays=5):
    """
    Generates a parallel beam where ray density follows a Gaussian distribution.
    Higher ray density in the center = Higher intensity.
    
    waist_radius: The 'sigma' or width of the beam (approx 1/e^2 width)
    """
    rays = []
    
    source_pos = np.array(source_pos)
    vec_to_target = np.array(target_element_centre) - source_pos
    direction = vec_to_target / np.linalg.norm(vec_to_target)
    tangent = np.array([-direction[1], direction[0]])
    
    # Generate Gaussian distributed offsets  
    offsets = np.random.normal(loc=0.0, scale=waist_radius/2.0, size=num_rays) 
    offsets = np.clip(offsets, -1.5*waist_radius, 1.5*waist_radius) # Clip values to 3*sigma to avoid outliers missing the optics entirely
    offsets.sort() # Sort for cleaner plotting (optional, but looks better if lines don't cross in array order)

    for lam, color in wavelengths:
        for offset in offsets:
            start_pos = source_pos + (tangent * offset)
            rays.append(Ray(start_pos, direction, lam, color))
            
    return rays

def generate_gaussian_beam_deter(wavelengths, source_pos, target_element_centre, waist_radius, num_rays=5):
    """
    Generates a Gaussian beam using DETERMINISTIC sampling.
    Visuals will be perfectly smooth and symmetric.
    """
    rays = []
    
    source_pos = np.array(source_pos)
    vec_to_target = np.array(target_element_centre) - source_pos
    dist = np.linalg.norm(vec_to_target)
    direction = vec_to_target / dist
    tangent = np.array([-direction[1], direction[0]])
    
    probs = np.linspace(1.0 / (num_rays + 1), 1.0 - 1.0 / (num_rays + 1), num_rays) # Create evenly spaced probabilities from 0 to 1 (excluding edges to avoid infinity)
    z_scores = ndtri(probs) # This tells us exactly how many standard deviations away each ray should be
    offsets = z_scores * (waist_radius / 2.0) # Scale by the beam width (Sigma = waist / 2)
    
    for lam, color in wavelengths:
        for offset in offsets:
            start_pos = source_pos + (tangent * offset)
            rays.append(Ray(start_pos, direction, lam, color))
            
    return rays

def plot_system(rays, elements, ax):
    
    segments = []
    colors = []
    
    for ray in rays:
        path = np.array(ray.path) # Shape (N, 2)
        segments.append(path) # Create ONE object representing ALL rays
        colors.append(ray.color)

    lc = LineCollection(segments, colors=colors, linewidths=1, alpha=0.5)
    ax.add_collection(lc)

    for el in elements:
        el.plot(ax)

    ax.autoscale() 
    ax.margins(0.05)

def screen_result(screen, rays, ax=None):
    """
    Analyzes rays that hit a specific screen.
    
    Args:
        screen: The Screen object to analyze.
        rays: List of Ray objects.
        ax: (Optional) Matplotlib axis to plot the mean position.
        
    Returns:
        dict: Statistics about the spot (mean, variance, rms_radius, count)
    """
    # Filter rays that were detected by this specific screen
    hits = [r.pos for r in rays if getattr(r, 'detected', False) == screen.name]
    
    if not hits:
        print(f"--- Result for Screen '{screen.name}' ---")
        print("No rays hit this screen.")
        return None

    # Convert to numpy array for vector math
    hits_arr = np.array(hits)
    
    # Calculate Statistics    
    mean_pos = np.mean(hits_arr, axis=0) # Centroid: This is the center of the light spot
    variance = np.var(hits_arr, axis=0) # Variance
    std_dev = np.std(hits_arr, axis=0) # Std. deviation
    diffs = hits_arr - mean_pos
    dist_sq = np.sum(diffs**2, axis=1) # Squared distance for each ray
    rms_radius = np.sqrt(np.mean(dist_sq)) # RMS Spot Radius (The most standard optical metric)
    max_dist = np.sqrt(np.max(dist_sq)) # Geometric Span (Max diameter approx)

    # Print Report
    print(f"\n--- Analysis for Screen: '{screen.name}' ---")
    print(f"Rays Captured: {len(hits)} / {len(rays)}")
    print(f"Centroid (Global): {mean_pos}")
    print(f"RMS Spot Radius:   {rms_radius:.6f} units")
    print(f"Max Spot Radius:   {max_dist:.6f} units")
    print(f"Variance (x, y):   {variance}")

    # Plotting (if ax is provided)
    if ax:
        # Plot the Centroid (Red Cross)
        ax.plot(mean_pos[0], mean_pos[1], 'ro', markersize=1, markeredgewidth=2, label='Centroid')
        
        # Optional: Plot a circle representing the RMS radius
        # (Visually approximate as a circle, though the spot might be astigmatic)
        spot_circle = plt.Circle((mean_pos[0], mean_pos[1]), rms_radius, 
                                 color='r', fill=False, linestyle='--', alpha=0.5, label='RMS Spot')
        ax.add_patch(spot_circle)
        
        # Add a text annotation near the spot
        # ax.text(mean_pos[0], mean_pos[1] + rms_radius, f"RMS: {rms_radius:.4f}", 
                # color='red', fontsize=8, ha='center', va='bottom')

    return {
        'count': len(hits),
        'mean_pos': mean_pos,
        'rms_radius': rms_radius,
        'variance': variance
    }

def convert_elements_to_array(elements):
    """
    Converts a list of OpticalElement objects into a single contiguous 
    NumPy array (float32) ready for further C++/GPU processing.

    Args:
        elements (list): List of OpticalElement objects (ThinLens, Prism, etc.)

    Returns:
        np.ndarray: A (N, M) array where:
            N = Number of elements
            M = Width of the largest element struct (padded with zeros)
    """
    if not elements: # Check for no elements
        return np.empty((0, 0), dtype=np.float32)

    raw_rows = []
    max_width = 30

    # Call the element's own packaging logic 
    for i, el in enumerate(elements):       
        row = el.package(i) # This returns a 1D array of floats        
        row = np.array(row, dtype=np.float32).flatten() # Ensure it's a flat list/array        
        raw_rows.append(row)

    packed_array = np.zeros((len(elements), max_width), dtype=np.float32) # Initialize the main buffer separately to maintain the zero padding

    # Fill the Buffer
    for i, row in enumerate(raw_rows):
        current_width = len(row)
        packed_array[i, :current_width] = row # Copy data into the corresponding slot

    return packed_array

def convert_rays_to_array(rays):
    """
    Converts a list of Ray objects into a contiguous NumPy array 
    ready for further C++/GPU processing.
    
    Args:
        rays (list): List of Ray objects.
        
    Returns:
        np.ndarray: A (N, 7) array of float32.
                    Format per row: [-1, 1, wav, x, y, dx, dy]
    """
    if not rays: # Check for no rays
        return np.empty((0, 7), dtype=np.float32)

    # Initialize the main buffer
    count = len(rays)
    packet_size = 7    
    packed_array = np.zeros((count, packet_size), dtype=np.float32) 

    # Fill the buffer
    for i, r in enumerate(rays):
        packed_array[i] = r.package()
        
    return packed_array

def run_simulation(rays, elements, bounces, use_gpu):

    # Initilise data and storage arrays
    lib = _get_engine(prefer_gpu=use_gpu)
    num_elements = len(elements)
    num_rays = len(rays)
    elements_ = convert_elements_to_array(elements)
    rays_ = convert_rays_to_array(rays)
    intersection_array = np.full(2 * num_rays * (bounces + 1), -np.inf, dtype=np.float32) # Initialized to -inf allows us to easily filter out unused "empty" bounces later
    record_array = np.full(num_rays, -1, dtype=np.float32) # To store which element ID/Index captured the ray (init to -1 for "Miss")

    # Call C++ by passing pointers to the numpy arrays
    lib.simulate_c(
        rays_.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
        ctypes.c_int(num_rays),
        elements_.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
        ctypes.c_int(num_elements),
        ctypes.c_int(bounces),
        intersection_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        record_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    )

    # Unpack Results
    stride = 2 * (bounces + 1)
    i = 0
    while(i < num_rays):

        # Decode element that detected the ray
        caught_idx = int(record_array[i])
        if caught_idx != -1 and caught_idx < num_elements:
            rays[i].detected = elements[caught_idx].name
        else:
            rays[i].detected = False

        # Decode Ray Path
        start = i * stride
        end = start + stride
        raw_path = intersection_array[start:end].reshape((bounces + 1, 2)) # Extract the slice and reshape it into a list of (x,y) pairs
        valid_mask = np.isfinite(raw_path[:, 0]) # Filter out the rows that are still -inf (bounces that never happened)
        rays[i].path = raw_path[valid_mask] # Assign the clean (N, 2) array to the ray object
        rays[i].pos = rays[i].path[len(rays[i].path) - 1]
        
        i += 1

# ==========================================
# Base Optical Element
# ==========================================

class OpticalElement:
    def __init__(self, name, center, normal, aperture):
        self.name = name
        self.center = np.array(center, dtype=float)
        
        # Normalize the normal
        n_len = np.linalg.norm(normal)
        if n_len == 0: raise ValueError("Normal cannot be zero")
        self.normal = np.array(normal, dtype=float) / n_len
        
        self.aperture = aperture

        # Tangent: Rotate normal by 90 degrees anticlockwise: (-y, x)
        self.tangent = np.array([-self.normal[1], self.normal[0]])

    def package(self, i):
        raise NotImplementedError

    def plot(self, ax):
        raise NotImplementedError

# ==========================================
# Geometry Mixins / Base Classes
# ==========================================

class FlatOpticalElement(OpticalElement):
    """
    Handles intersection and plotting for flat surfaces (Planes).
    """
    def plot(self, ax):
        # Draw a straight line
        half_vec = self.tangent * (self.aperture / 2.0)
        p1 = self.center + half_vec
        p2 = self.center - half_vec
        
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=2)
        
                 
        # Label
        label_pos = self.center - half_vec * 1.2 # Label behind
        ax.text(label_pos[0], label_pos[1], self.name, 
                ha='center', va='center', fontsize=8, color='blue', rotation=0)

class SphericalOpticalElement(OpticalElement):
    """
    Handles intersection and plotting for Spherical surfaces.
    """
    def __init__(self, name, center, normal, aperture, radius):
        super().__init__(name, center, normal, aperture)
        self.radius = radius 
        
        # R > 0: Center is in direction of Normal by convention
        # Calculate Center of Curvature (CC)
        # CC = Vertex + R * Normal
        self.cc = self.center + self.normal * self.radius

        # Clamp Aperture if it is too big
        if self.aperture > 2 * self.radius:
            self.aperture = 2 * self.radius
            # print(f"Clamping the aperture of {self.name} to {self.aperture}.")

    def plot(self, ax):
        # Plotting an Arc using matplotlib patches
        # Arc requires: center (xy), width, height, angle (rotation), theta1, theta2
        
        # Calculate angular aperture (theta) and then the plotting extent (theta1 and theta2)
        ratio = np.clip((self.aperture / 2.0) / abs(self.radius), -1.0, 1.0)
        half_angle_rad = np.arcsin(ratio)
        half_angle_deg = np.degrees(half_angle_rad)
        vec_c_to_v = self.center - self.cc
        base_angle = np.degrees(np.arctan2(vec_c_to_v[1], vec_c_to_v[0]))
        theta1 = base_angle - half_angle_deg
        theta2 = base_angle + half_angle_deg
        
        arc = patches.Arc(self.cc, 
                          2*abs(self.radius), 2*abs(self.radius), 
                          angle=0.0, 
                          theta1=theta1, theta2=theta2, 
                          color='black', lw=2)
        ax.add_patch(arc)
        
        # Label
        pos = self.center - 0.6 * self.aperture * self.tangent
        ax.text(pos[0], pos[1], self.name, 
                ha='center', va='bottom', fontsize=8, color='blue')

class RefractiveOpticalElement(OpticalElement):
    """
    Base class for elements that transmit and refract light.
    Handles refractive index lookup and Snell's Law physics.
    """
    def __init__(self, name, center, normal, aperture, refractive_index):
        super().__init__(name, center, normal, aperture)
        self.rcase = 0
        self.refractive_index = -1

        # Case 1: Fixed Value (Simple float/int)
        if isinstance(refractive_index, (float, int)):
            self.rcase = 1
            self.refractive_index = [float(refractive_index), 0.0, 0.0, 0.0, 0.0, 0.0]
            return

        # Case 2: Resolve Coefficients
        coeffs = None
        
        # If it's a string, look it up in the DB provided
        if isinstance(refractive_index, str):
            if refractive_index in GLASS_DB:
                coeffs = GLASS_DB[refractive_index]
            else:
                raise ValueError(f"Unknown glass type: {refractive_index}")
        
        # If it's already a dictionary, use it directly
        elif isinstance(refractive_index, dict):
            coeffs = refractive_index
            
        # If it's already a list, take the list directly
        elif isinstance(refractive_index, (list, tuple)) and len(refractive_index) == 6:
             self.rcase = 2
             self.refractive_index = [float(x) for x in refractive_index]
             return

        # Execute Sellmeier Logic
        if coeffs is not None:
            self.rcase = 2
            self.refractive_index = [
                coeffs['B1'], coeffs['B2'], coeffs['B3'], 
                coeffs['C1'], coeffs['C2'], coeffs['C3']
            ]
            return

        # Fallback Error (Fixed to show the INPUT type)
        raise ValueError(f"Invalid refractive index type: {type(refractive_index)}")

# ==========================================
# Optical Elements
# ==========================================

class ParabolicMirror(OpticalElement):
    """
    A parabolic mirror defined by its focal length and aperture.
    Geometry: y^2 = 4 * f * x (in local coordinates).
    Perfectly focuses parallel rays to the focal point without spherical aberration.
    """
    def __init__(self, name, center, normal, aperture, focal_length):
        super().__init__(name, center, normal, aperture)
        self.focal_length = focal_length

        # We need a rotation matrix to go from World -> Local (Vertex at 0,0, Axis along +X)
        self.u_axis = self.normal / np.linalg.norm(self.normal) # Focal Axis (Local X)
        self.v_axis = np.array([-self.u_axis[1], self.u_axis[0]]) # Tangent (Local Y): rotated 90 deg from normal anticlockwise
        self.R_world_to_local = np.array([self.u_axis, self.v_axis]) # Rotation Matrix (World to Local)
        self.R_local_to_world = self.R_world_to_local.T # Rotation Matrix (Local to World): Transpose of above
        self.sagitta = (self.aperture)**2 / (16 * self.focal_length)

    def package(self, i):
        return np.array([0, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture, 
                        self.focal_length, self.sagitta, self.u_axis[0], self.u_axis[1], self.v_axis[0], self.v_axis[1], 
                        self.R_world_to_local[0][0], self.R_world_to_local[0][1], self.R_world_to_local[1][0], self.R_world_to_local[1][1],
                        self.R_local_to_world[0][0], self.R_local_to_world[0][1], self.R_local_to_world[1][0], self.R_local_to_world[1][1],])

    def plot(self, ax):

        # Generate points for the parabola in Local Frame
        v_points = np.linspace(-self.aperture/2, self.aperture/2, 50) # v goes from -aperture/2 to +aperture/2
        u_points = (v_points**2) / (4 * self.focal_length)
        local_points = np.vstack((u_points, v_points))
        
        # Transform to World
        center_reshaped = self.center[:, np.newaxis] # Broadcast the center to shape (2, 50)
        world_points = center_reshaped + np.dot(self.R_local_to_world, local_points) # world_points = Center + R * local_points
        
        ax.plot(world_points[0, :], world_points[1, :], color='black', lw=2)
        
        # Label
        pos = self.center - 0.6 * self.aperture * self.tangent
        ax.text(pos[0], pos[1], self.name, 
                ha='center', va='top', fontsize=8, color='blue')

class FlatMirror(FlatOpticalElement):
    def package(self, i):
        return np.array([1, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture])

class SphericalMirror(SphericalOpticalElement):
    def package(self, i):
        return np.array([2, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture, 
                        self.radius, self.cc[0], self.cc[1]])

class Screen(FlatOpticalElement):
    def package(self, i):
        return np.array([3, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture])

class ThinLens(FlatOpticalElement):
    """
    Simulates a lens using the thin-lens approximation on a flat plane.
    (Geometric intersection is flat, but phase/bending mimics curvature)
    """
    def __init__(self, name, center, normal, aperture, focal_length):
        super().__init__(name, center, normal, aperture)
        self.focal_length = focal_length

    def package(self, i):
        return np.array([4, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture, self.focal_length])

class TransmissionGrating(FlatOpticalElement):
    def __init__(self, name, center, normal, aperture, lines_per_mm, order=1):
        super().__init__(name, center, normal, aperture)
        self.d = 1e-6 * (1000 / lines_per_mm)
        self.order = order

    def package(self, i):
        return np.array([5, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture, self.d, self.order])

class ReflectiveGrating(FlatOpticalElement):
    def __init__(self, name, center, normal, aperture, lines_per_mm, order=1):
        super().__init__(name, center, normal, aperture)
        self.d = 1e-6 * (1000 / lines_per_mm)
        self.order = order
    
    def package(self, i):
        return np.array([6, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture, self.d, self.order])

class Slab(RefractiveOpticalElement):
    def __init__(self, name, center, normal, aperture, refractive_index, thickness):
        super().__init__(name, center, normal, aperture, refractive_index)
        self.thickness = thickness
        
        # Define geometry of faces for calculation        
        half_vec = self.normal * (thickness / 2.0)
        self.c1 = self.center - half_vec
        self.n1 = -self.normal 
        self.c2 = self.center + half_vec
        self.n2 = self.normal

    def package(self, i):
        return np.array([7, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture,
                         self.thickness, self.c1[0], self.c1[1], self.n1[0], self.n1[1],
                         self.c2[0], self.c2[1], self.n2[0], self.n2[1], self.rcase,
                         self.refractive_index[0], self.refractive_index[1], self.refractive_index[2], 
                         self.refractive_index[3], self.refractive_index[4], self.refractive_index[5]])

    def plot(self, ax):
        # Calculate corner points for the rectangle
        h_vec = self.tangent * (self.aperture / 2.0)
        p1_top = self.c1 + h_vec
        p1_bot = self.c1 - h_vec
        p2_top = self.c2 + h_vec
        p2_bot = self.c2 - h_vec
        
        # Draw box
        poly = np.array([p1_top, p2_top, p2_bot, p1_bot])
        patch = patches.Polygon(poly, closed=True, facecolor='lightblue', edgecolor='black', alpha=0.3)
        ax.add_patch(patch)
        
        pos = self.center - 0.6 * self.aperture * self.tangent
        ax.text(pos[0], pos[1], self.name, ha='center', va='center', fontsize=8, color='blue')

class Lens(RefractiveOpticalElement):
    def __init__(self, name, center, normal, aperture, refractive_index, R1, R2, thickness):
        """
        Assuming the normal points towards the right of the lens, we use the standard lens convention:
        R1: Radius of curvature of the first surface (Left).
            > 0: Convex (bulges left, center to right)
            < 0: Concave (caves left, center to left)
        R2: Radius of curvature of the second surface (Right).
            > 0: Concave (caves right, center to right)
            < 0: Convex (bulges right, center to left)
        """
        super().__init__(name, center, normal, aperture, refractive_index)
        self.R1 = R1
        self.R2 = R2
        self.thickness = thickness
        
        # 1. Calculate Geometry
        half_vec = self.normal * (thickness / 2.0)
        self.v1 = self.center - half_vec # Front/Left vertex
        self.v2 = self.center + half_vec # Back/Right vertex
        self.cc1 = self.v1 + self.normal * self.R1
        self.cc2 = self.v2 + self.normal * self.R2 
        
        # Safe aperture clamping
        try:
            d = np.linalg.norm(self.cc1 - self.cc2)
            r1, r2 = abs(R1), abs(R2)
            
            if d < (r1 + r2) and d > abs(r1 - r2): # Intersection of spheres (Meniscus or Biconvex) case
                if d < 1e-9:
                    h = min(r1, r2)
                else:
                    x = (r1**2 - r2**2 + d**2) / (2*d)
                    val = r1**2 - x**2
                    h = np.sqrt(max(0, val)) # Stability clamp
                
                max_physical = 2.0 * h
                if self.aperture > max_physical:
                    self.aperture = max_physical
            else: # No intersection might also require clamping
                h = min(r1, r2)
                max_physical = 2.0 * h
                if self.aperture > max_physical:
                    self.aperture = max_physical
        except Exception:
            pass 

    def package(self, i):
        return np.array([8, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture,
                         self.thickness, self.R1, self.R2, self.v1[0], self.v1[1],
                         self.v2[0], self.v2[1], self.cc1[0], self.cc1[1], self.cc2[0], self.cc2[1], self.rcase,
                         self.refractive_index[0], self.refractive_index[1], self.refractive_index[2], 
                         self.refractive_index[3], self.refractive_index[4], self.refractive_index[5]])

    def plot(self, ax):

        # Plotting thick lens as a polygon or closed shape is complex with patches.Arc
        # Simpler approach: Calculate points along the surface and draw polygon.
        
        def get_arc_points(cc, r, v_pos):

            # Generate points for the arc using its base angle
            vec_c_v = v_pos - cc
            base_angle = np.arctan2(vec_c_v[1], vec_c_v[0])
            h = np.linspace(-self.aperture/2, self.aperture/2, 20) # Height range: -aperture/2 to +aperture/2
            
            pts = []
            for hi in h:
                
                # Delta angle for height h
                ratio = np.clip(hi / r, -1.0, 1.0)
                alpha = np.arcsin(ratio)
                
                theta = base_angle + alpha
                
                px = cc[0] + r * np.cos(theta)
                py = cc[1] + r * np.sin(theta)
                pts.append([px, py])
            
            return pts

        pts1 = get_arc_points(self.cc1, abs(self.R1), self.v1)
        pts2 = get_arc_points(self.cc2, abs(self.R2), self.v2)
        
        # Combine points: Pts1 (top to bottom) -> Pts2 (bottom to top) to close loop        
        poly_pts = pts1[::-1] + pts2
        
        poly = patches.Polygon(poly_pts, closed=True, facecolor='lightblue', edgecolor='black', alpha=0.3)
        ax.add_patch(poly)
        
        # Label
        pos = self.center - 0.6 * self.aperture * self.tangent
        ax.text(pos[0], pos[1], self.name, ha='center', va='center', fontsize=8, color='blue')

class Prism(RefractiveOpticalElement):
    def __init__(self, name, center, normal, refractive_index, apex_angle, side_length):

        # We pass side_length as aperture to parent, though we define specific faces below
        super().__init__(name, center, normal, aperture=side_length, refractive_index=refractive_index)
        
        self.apex_angle = np.radians(apex_angle)
        self.side_length = side_length
        half_angle = self.apex_angle / 2.0
        self.height = self.side_length * np.cos(half_angle)
        self.base_width = 2 * self.side_length * np.sin(half_angle)
        
        # Define Vertices relative to the Geometric Center (Centroid)
        # The centroid is located at 2/3 height from apex, 1/3 height from base.
        vec_c_to_apex = -self.normal * (2.0 / 3.0 * self.height)
        self.vec_c_to_base = self.normal * (1.0 / 3.0 * self.height)
        self.p_apex = self.center + vec_c_to_apex
        vec_half_base = self.tangent * (self.base_width / 2.0)       
        self.p_base_top = self.center + self.vec_c_to_base + vec_half_base
        self.p_base_bot = self.center + self.vec_c_to_base - vec_half_base
        
        # Define Face Normals (Must point OUTWARD)
        self.n_base = self.normal # Points out of the base side
        
        # Calculate normals for legs by rotating the face vectors
        
        # Helper function to get normal for segment p1->p2
        def get_outward_normal(p1, p2, interior_point):
            edge = p2 - p1

            # orthogonal vector (-y, x)
            ortho = np.array([-edge[1], edge[0]])
            ortho = ortho / np.linalg.norm(ortho)

            # Check direction: dot product with vector to interior should be negative
            if np.dot(ortho, interior_point - p1) > 0:
                ortho = -ortho
            return ortho

        self.n_top = get_outward_normal(self.p_apex, self.p_base_top, self.center)
        self.n_bot = get_outward_normal(self.p_base_bot, self.p_apex, self.center)

    def package(self, i):
        return np.array([9, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture,
                         self.apex_angle, self.side_length, self.height, self.base_width,
                         self.p_apex[0], self.p_apex[1], self.p_base_top[0], self.p_base_top[1], self.p_base_bot[0], self.p_base_bot[1], 
                         self.n_base[0], self.n_base[1], self.n_top[0], self.n_top[1], self.n_bot[0], self.n_bot[1], self.rcase,
                         self.refractive_index[0], self.refractive_index[1], self.refractive_index[2], 
                         self.refractive_index[3], self.refractive_index[4], self.refractive_index[5]])


    def plot(self, ax):
        # Define vertices for polygon
        poly_points = np.array([self.p_apex, self.p_base_top, self.p_base_bot])
        
        # Draw Triangle
        patch = patches.Polygon(poly_points, closed=True, facecolor='cyan', edgecolor='blue', alpha=0.3)
        ax.add_patch(patch)
        
        # Label
        pos = self.center + 1.2 * self.vec_c_to_base
        ax.text(pos[0], pos[1], self.name, ha='center', va='center', fontsize=8, color='darkblue')

class CircularAperture(OpticalElement):
    """
    A circular stop. 
    Rays inside the radius PASS THROUGH (are ignored by this element).
    Rays outside the radius are BLOCKED (absorbed).
    """
    def __init__(self, name, center, normal, radius, outer_radius=None):

        # We define the parent 'aperture' as the diameter of the hole
        super().__init__(name, center, normal, aperture=radius*2)
        self.radius = radius
        self.outer_radius = outer_radius if outer_radius else radius * 3.0 # Default to 3x the hole size if not specified

    def package(self, i):
        return np.array([10, i, self.center[0], self.center[1], self.normal[0], self.normal[1], self.aperture,
                         self.radius, self.outer_radius])

    def plot(self, ax):
        
        # "Top" Plate: From +Radius to +OuterRadius
        p_top_start = self.center + self.tangent * self.radius
        p_top_end   = self.center + self.tangent * self.outer_radius
        
        # "Bottom" Plate: From -Radius to -OuterRadius
        p_bot_start = self.center - self.tangent * self.radius
        p_bot_end   = self.center - self.tangent * self.outer_radius
        
        # Draw the lines (Thick black lines to indicate blocking)
        ax.plot([p_top_start[0], p_top_end[0]], [p_top_start[1], p_top_end[1]], 
                color='black', linewidth=3)
        ax.plot([p_bot_start[0], p_bot_end[0]], [p_bot_start[1], p_bot_end[1]], 
                color='black', linewidth=3)
        
        # Label
        text_pos = self.center - 1.2 * self.outer_radius * self.tangent
        ax.text(text_pos[0], text_pos[1], self.name, 
                ha='center', va='center', fontsize=8, color='darkblue')

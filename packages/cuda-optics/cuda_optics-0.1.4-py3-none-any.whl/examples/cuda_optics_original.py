import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from scipy.special import ndtri  # for deterministic gaussian beam

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
        self.path = [(self.pos.copy())]
        self.terminated = False
        self.detected = False

    def update(self, new_pos, new_dir=None):
        """Updates ray state after interaction."""
        self.pos = new_pos
        self.path.append(new_pos.copy())
        if new_dir is not None:
            # Normalize new direction
            self.dir = new_dir / np.linalg.norm(new_dir)
    
    def terminate(self, pos):
        """Ends the ray at a specific position (e.g., absorbed by screen)."""
        self.pos = pos
        self.path.append(pos.copy())
        self.terminated = True

    def detect(self, name):
        """
        Detects rays falling on a screen. If a ray ends at a particular screen, its detected attribute
        stores the name of the screen. Otherwise this attribute remains as False.
        """
        self.detected = name

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

    def interact(self, ray):
        """
        Template method: 
        1. Get geometric intersection (implemented in subclasses)
        2. Apply Physics (implemented in subclasses)
        """
        hit_pos, normal_at_hit = self.get_intersection_and_normal(ray) # Implemented separately for specific cases
        
        if hit_pos is not None:
            new_dir, stop = self.physics(ray, hit_pos, normal_at_hit) # Implemented separately for specific cases
            if stop:
                ray.terminate(hit_pos)
            else:
                ray.update(hit_pos, new_dir)
            return True
        return False

    def get_intersection_and_normal(self, ray):
        raise NotImplementedError

    def physics(self, ray, hit_pos, normal_at_hit):
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
    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None

        # If the newer intersection point is P, then the following is true: 
        # Ray: P = O + tD
        # Plane: (P - C) . N = 0
        # So, t = ((C - O) . N) / (D . N)
        denom = np.dot(ray.dir, self.normal)
        
        if abs(denom) < 1e-12: return None, None # Parallel check to avoid floating point errors

        vec_to_center = self.center - ray.pos
        t = np.dot(vec_to_center, self.normal) / denom 
        
        if t < 1e-9: return None, None # Either the object is behind the ray or exactly at its position

        hit_pos = ray.pos + t * ray.dir # Calculation of actual position of hitting

        # Aperture Check (Project onto tangent)
        vec_to_hit = hit_pos - self.center
        local_height = np.dot(vec_to_hit, self.tangent)
        if abs(local_height) > self.aperture / 2.0:
            return None, None
            
        return hit_pos, self.normal # For a flat surface, normal is constant

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None

        # If the intersection happens at the point O + tD, then:
        # |O + tD - CC|^2 = R^2 for sphere
        # Define L = O - CC for ray
        # Solve, t^2 + 2(D.L)t + (L.L - R^2) = 0 for t using the Quadratic Formula
        L = ray.pos - self.cc
        a = 1.0 
        b = 2.0 * np.dot(ray.dir, L)
        c = np.dot(L, L) - self.radius**2
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return None, None # Missed the entire sphere
            
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        # Find smallest positive t > epsilon for the nearest/first intersection
        epsilon = 1e-9
        ts = [t1, t2]
        ts_final = []

        r_abs = abs(self.radius)
        
        # Calculate the Cosine Threshold for Aperture check
        # cos(theta_max) = sqrt(1 - (aperture_radius / sphere_radius)^2)
        # Any hit with cos(theta) < threshold is outside the aperture.
        # Any hit with cos(theta) < 0 is on the back (ghost) side.
        semi_aperture = self.aperture / 2.0
        ratio = min(1.0, semi_aperture / r_abs)
        min_cos_theta = np.sqrt(1.0 - ratio**2)
        axis_vec = self.center - self.cc # Define the Axis Vector of the physical cap (From CC to Vertex)
        axis_vec = axis_vec / np.linalg.norm(axis_vec) # Normailze

        for t in ts:
            if t > epsilon:
                hit_pos = ray.pos + t * ray.dir
                
                # Calculate vector from CC to this specific Hit
                hit_vec = hit_pos - self.cc
                hit_vec = hit_vec / r_abs # Normalize
                
                # Check the angle relative to the cap axis
                hit_cos = np.dot(axis_vec, hit_vec)
                if hit_cos >= min_cos_theta:
                    ts_final.append([t, hit_pos])
        
        if not ts_final:
            return None, None # None of the t values are eligible to be taken forward
            
        hit_pos = min(ts_final, key = lambda x: x[0])[1]
        
            
        # Normal Calculation
        # For a sphere, normal is vector from Center of Curvature to Hit Position
        # Direction depends on sign of radius? 
        # Geometric normal points outward from sphere center.
        radial_vec = hit_pos - self.cc
        normal_at_hit = radial_vec / np.linalg.norm(radial_vec)
        
        # Flip normal if direction of normal and ray is within 180 degrees, to maintain consistent "surface normal" direction
        if np.dot(normal_at_hit, ray.dir) > 0:
            normal_at_hit = -normal_at_hit
            
        return hit_pos, normal_at_hit

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
        self.refractive_index = refractive_index

    def get_index(self, wavelength_nm):
        """
        Resolves refractive index n for a specific wavelength.
        """
        # Case 1: Fixed Value (Simple float/int)
        if isinstance(self.refractive_index, (float, int)):
            return float(self.refractive_index)

        # Case 2: Resolve Coefficients
        coeffs = None
        
        # If it's a string, look it up in the DB provided
        if isinstance(self.refractive_index, str):
            if self.refractive_index in GLASS_DB:
                coeffs = GLASS_DB[self.refractive_index]
            else:
                raise ValueError(f"Unknown glass type: {self.refractive_index}")
    
        # If it's already a dictionary, use it directly
        elif isinstance(self.refractive_index, dict):
            coeffs = self.refractive_index

        # Execute Sellmeier Logic
        if coeffs is not None:
            lam_sq = (wavelength_nm / 1000.0) ** 2
            n2 = 1 + (coeffs['B1'] * lam_sq) / (lam_sq - coeffs['C1']) + \
                     (coeffs['B2'] * lam_sq) / (lam_sq - coeffs['C2']) + \
                     (coeffs['B3'] * lam_sq) / (lam_sq - coeffs['C3'])
            return np.sqrt(n2)

        # Case 3: OpticalGlass Object (Duck typing)
        if hasattr(self.refractive_index, 'rindex'):
            return self.refractive_index.rindex(wavelength_nm)

        # If we reached here, nothing matched.
        raise ValueError(f"Invalid refractive index type: {type(self.refractive_index)}")

    def physics(self, ray, hit_pos, normal_at_hit):
        """
        Applies Vector Snell's Law.
        """

        # Determine n1, n2, eff_normal and cos_theta1 
        # We assume the normals provided point OUT of the object.
        dot_product = np.dot(ray.dir, normal_at_hit)
        n_glass = self.get_index(ray.wavelength) # Initialise both
        n_air = 1.0
        if dot_product < 0: # Ray is entering the object (opposing the outward normal)
            n1 = n_air
            n2 = n_glass
            eff_normal = normal_at_hit # Use normal as is
            cos_theta1 = -dot_product  # Cos must be positive
        else: # Ray is exiting the object (aligned with outward normal)
            n1 = n_glass
            n2 = n_air
            eff_normal = -normal_at_hit # Flip normal to point into n1 for standard formula
            cos_theta1 = dot_product

        # Apply standard Snell's law: v_out = r*v_in + (r*c - sqrt(1 - r^2(1-c^2))) * n
        # where r = n1/n2 and c = - normal . v_in (which is cos_theta1)
        r = n1 / n2
        sin2_theta1 = 1.0 - cos_theta1**2
        term_inside_sqrt = 1.0 - (r**2 * sin2_theta1)

        if term_inside_sqrt < 0: # Check for Total Internal Reflection (TIR)

            # Standard reflection: v_out = v_in - 2(v_in . n)n
            # We use the original normal_at_hit logic for reflection
            reflect_normal = normal_at_hit if dot_product < 0 else -normal_at_hit
            new_dir = ray.dir - 2 * np.dot(ray.dir, reflect_normal) * reflect_normal
            return new_dir, False

        # Continue the calculation for refraction
        sqrt_term = np.sqrt(term_inside_sqrt)
        new_dir = r * ray.dir + (r * cos_theta1 - sqrt_term) * eff_normal
        new_dir = new_dir / np.linalg.norm(new_dir) # Normalize
        
        return new_dir, False

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None
        
        # Transform the ray to the local frame of the parabola Through rotation matrix, to solve for the intersection.
        rel_pos = ray.pos - self.center # Relative position
        p_local = np.dot(self.R_world_to_local, rel_pos)
        d_local = np.dot(self.R_world_to_local, ray.dir)
        ux, uy = p_local[0], p_local[1] # Using ux, uy for local x,y
        dx, dy = d_local[0], d_local[1]
        
        # To solve for intersection, assume the parameter t and simultaneously solve for the following constraints:
        # Ray: u(t) = ux + t*dx, v(t) = vy + t*dy
        # Parabola: (vy + t*dy)^2 = 4f * (ux + t*dx)
        # Expand: dy^2*t^2 + 2*vy*dy*t + vy^2 = 4f*ux + 4f*dx*t
        # Solve the Quadratic At^2 + Bt + C = 0
        fx = self.focal_length
        A = dy**2
        B = 2 * uy * dy - 4 * fx * dx
        C = uy**2 - 4 * fx * ux
        if abs(A) < 1e-9: # Linear case (Ray parallel to axis, rare for parabolic mirror unless entering from side)
            if abs(B) < 1e-9: return None, None # Avoid division be zero
            ts = [-C / B]
        else:
            discriminant = B**2 - 4*A*C
            if discriminant < 0: return None, None # No intersection
            
            sqrt_disc = np.sqrt(discriminant)
            ts = [(-B - sqrt_disc) / (2*A), (-B + sqrt_disc) / (2*A)]
            
        # Filter through Aperture check
        valid_hits = []
        for t in ts:
            if t > 1e-9:

                # Calc hit in local
                hit_u = ux + t * dx
                hit_v = uy + t * dy
                
                # Check Aperture (based on v height)
                if abs(hit_v) <= self.aperture / 2.0:
                    valid_hits.append((t, hit_u, hit_v))
        if not valid_hits: return None, None
        
        # Get closest hit
        best = min(valid_hits, key=lambda x: x[0])
        t_hit, u_hit, v_hit = best
        
        # Calculate Normal as  (-4f, 2v) 
        n_local = np.array([-4 * fx, 2 * v_hit])
        n_local = n_local / np.linalg.norm(n_local)
        
        # Transform Normal and Hit back to World using the reverse matrix
        hit_pos = ray.pos + t_hit * ray.dir
        normal_world = np.dot(self.R_local_to_world, n_local)
        
        # Ensure normal opposes ray direction for proper reflection calculation
        if np.dot(normal_world, ray.dir) > 0:
            normal_world = -normal_world
            
        return hit_pos, normal_world

    def physics(self, ray, hit_pos, normal_at_hit):

        # Standard Reflection
        dot = np.dot(ray.dir, normal_at_hit)
        new_dir = ray.dir - 2 * dot * normal_at_hit
        return new_dir, False

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
    def physics(self, ray, hit_pos, normal_at_hit):

        # Standard Reflection
        dot = np.dot(ray.dir, normal_at_hit)
        new_dir = ray.dir - 2 * dot * normal_at_hit
        return new_dir, False

class SphericalMirror(SphericalOpticalElement):
    def physics(self, ray, hit_pos, normal_at_hit):

        # Standard reflection
        dot = np.dot(ray.dir, normal_at_hit)
        new_dir = ray.dir - 2 * dot * normal_at_hit
        return new_dir, False

class Screen(FlatOpticalElement):
    def physics(self, ray, hit_pos, normal_at_hit):
        ray.detect(self.name) # Activate the detected parameter
        return None, True # Terminate

class ThinLens(FlatOpticalElement):
    """
    Simulates a lens using the thin-lens approximation on a flat plane.
    (Geometric intersection is flat, but phase/bending mimics curvature)
    """
    def __init__(self, name, center, normal, aperture, focal_length):
        super().__init__(name, center, normal, aperture)
        self.focal_length = focal_length

    def physics(self, ray, hit_pos, normal_at_hit):
        # Calculate height from optical center to calculate the deflection angle (delta)
        vec_hit = hit_pos - self.center
        height = np.dot(vec_hit, self.tangent)
        delta = height / self.focal_length # Small angle approximation

        if np.dot(ray.dir, self.normal) < 0: delta = -delta
        
        # Rotate ray direction using matrix
        c, s = np.cos(-delta), np.sin(-delta)
        R = np.array(((c, -s), (s, c)))
        
        new_dir = np.dot(R, ray.dir)
        return new_dir, False

class TransmissionGrating(FlatOpticalElement):
    def __init__(self, name, center, normal, aperture, lines_per_mm, order=1):
        super().__init__(name, center, normal, aperture)
        self.d = 1e-6 * (1000 / lines_per_mm)
        self.order = order

    def physics(self, ray, hit_pos, normal_at_hit):

        # We need signed angle. Use Cross product or Atan2 in local frame.       
        cos_i = np.dot(ray.dir, self.normal)
        sin_i = np.dot(ray.dir, self.tangent)

        corrected_normal = self.normal
        corrected_order = self.order

        if cos_i < 0: # need to correct the direction of normal
            corrected_normal = -self.normal
            # corrected_order = -self.order # can be done if desired

        # Grating Eq: sin(theta_m) = sin(theta_i) + m*lam/d
        term = (corrected_order * ray.wavelength * 1e-9) / self.d
        sin_m = sin_i + term
        
        if abs(sin_m) > 1.0:
            return None, True # Evanescent / absorbed check
            
        theta_m = np.arcsin(sin_m)
        
        # Construct outgoing vector as u = cos(theta_m)*N + sin(theta_m)*T
        new_dir = np.cos(theta_m) * corrected_normal + np.sin(theta_m) * self.tangent
        
        return new_dir, False

class ReflectiveGrating(FlatOpticalElement):
    def __init__(self, name, center, normal, aperture, lines_per_mm, order=1):
        super().__init__(name, center, normal, aperture)
        self.d = 1e-6 * (1000 / lines_per_mm)
        self.order = order

    def physics(self, ray, hit_pos, normal_at_hit):

        # We need signed angle. Use Cross product or Atan2 in local frame.       
        cos_i = np.dot(ray.dir, self.normal)
        sin_i = np.dot(ray.dir, self.tangent)

        corrected_normal = self.normal
        corrected_order = self.order

        if cos_i >= 0: # need to correct the direction of normal
            corrected_normal = -self.normal
            # corrected_order = -self.order # can be done if desired

        # Grating Eq: sin(theta_m) = sin(theta_i) + m*lam/d
        term = (corrected_order * ray.wavelength * 1e-9) / self.d
        sin_m = sin_i + term
        
        if abs(sin_m) > 1.0:
            return None, True # Evanescent / absorbed check
            
        theta_m = np.arcsin(sin_m)
        
        # Construct outgoing vector as u = cos(theta_m)*N + sin(theta_m)*T
        new_dir = np.cos(theta_m) * corrected_normal + np.sin(theta_m) * self.tangent
        
        return new_dir, False

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None
        
        hits = []
        
        # Helper function to check a plane
        def check_plane(p_center, p_normal):
            denom = np.dot(ray.dir, p_normal)
            if abs(denom) < 1e-12: return None # parallel ray
            t = np.dot(p_center - ray.pos, p_normal) / denom
            if t < 1e-9: return None # Opposite ray / same point 
            
            # Aperture check
            hit_pos = ray.pos + t * ray.dir
            vec_to_hit = hit_pos - p_center
            h = np.dot(vec_to_hit, self.tangent)
            if abs(h) > self.aperture / 2.0: return None
            
            return (t, hit_pos, p_normal)

        # Check both faces and add to the hits array
        h1 = check_plane(self.c1, self.n1)
        h2 = check_plane(self.c2, self.n2)
        if h1: hits.append(h1)
        if h2: hits.append(h2)
        if not hits: return None, None
        
        # Return closest
        hits.sort(key=lambda x: x[0])
        return hits[0][1], hits[0][2]

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None

        hits = []

        # Helper for sphere intersection
        def check_sphere(cc, radius_signed, vertex, surface_side):
            radius = abs(radius_signed)
            
            # Basic Ray-Sphere Intersection
            L = ray.pos - cc
            b = 2.0 * np.dot(ray.dir, L)
            c = np.dot(L, L) - radius**2
            disc = b**2 - 4*c
            
            if disc < 0: return None
            
            sqrt_disc = np.sqrt(disc)
            ts = [(-b - sqrt_disc) / 2.0, (-b + sqrt_disc) / 2.0]
            
            best_hit = None
            min_t = float('inf')
            epsilon = 1e-9

            axis_vec = vertex - cc # Center reference axis for cosine check
            axis_vec = axis_vec / np.linalg.norm(axis_vec)

            ratio = min(1.0, (self.aperture / 2.0) / radius)
            min_cos_theta = np.sqrt(1.0 - ratio**2)

            for t in ts:
                if t > epsilon and t < min_t:
                    hit_pos = ray.pos + t * ray.dir
                    hit_vec = hit_pos - cc
                    hit_vec = hit_vec / radius # Normalized since magnitude is radius
                    
                    hit_cos_theta = np.dot(axis_vec, hit_vec) # Cosine calculated
                    
                    if hit_cos_theta >= min_cos_theta: # The hit is within the spherical cap defined by the aperture
                        best_hit = hit_pos
                        min_t = t
                    else: # Hit point missed the partial sphere
                        continue

            if best_hit is None: return None # The ray missed the partial sphere
                       
            n_raw = best_hit - cc # Calculate radial vector
            n_raw = n_raw / np.linalg.norm(n_raw)
            proj = np.dot(n_raw, self.normal)
            
            # If surface is Left (-1) and proj is positive, n_raw is pointing wrong. Flip.
            # If surface is Right (+1) and proj is negative, n_raw is pointing wrong. Flip.
            if (surface_side == -1 and proj > 0) or (surface_side == 1 and proj < 0):
                n_geo = -n_raw
            else:
                n_geo = n_raw
            
            return (min_t, best_hit, n_geo)

        # Check both surfaces
        h1 = check_sphere(self.cc1, abs(self.R1), self.v1, -1) 
        h2 = check_sphere(self.cc2, abs(self.R2), self.v2, 1)        
        if h1: hits.append(h1)
        if h2: hits.append(h2)
        
        if not hits: return None, None # The ray missed the lens
        
        hits.sort(key=lambda x: x[0])
        print(hits[0])
        print(ray.dir)
        return hits[0][1], hits[0][2]

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None
        
        hits = []
        
        # Helper to check a specific line segment (face)
        def check_face(p1, p2, face_normal):
            denom = np.dot(ray.dir, face_normal)
            if abs(denom) < 1e-12: return None
            
            t = np.dot(p1 - ray.pos, face_normal) / denom # Distance to plane
            if t < 1e-9: return None
            
            hit_pos = ray.pos + t * ray.dir
            
            # Segment Check: Is the hit point between p1 and p2?
            edge_vec = p2 - p1
            edge_len = np.linalg.norm(edge_vec)
            hit_vec = hit_pos - p1
            proj = np.dot(hit_vec, edge_vec) / edge_len # Dot product to find projection length * edge length

            corner_pad = 1e-4

            if 0 <= proj <= edge_len: # Check if projection is between 0 and length of edge
                if proj < corner_pad or proj > (edge_len - corner_pad): # Kill the ray
                    return (t, hit_pos, None)
                return (t, hit_pos, face_normal)
            
            return None

        # Check all 3 faces
        h1 = check_face(self.p_apex, self.p_base_top, self.n_top)
        if h1: hits.append(h1)
        h2 = check_face(self.p_base_bot, self.p_apex, self.n_bot)
        if h2: hits.append(h2)
        h3 = check_face(self.p_base_top, self.p_base_bot, self.n_base)
        if h3: hits.append(h3)
        
        if not hits: return None, None
        
        # Return closest hit
        hits.sort(key=lambda x: x[0])
        return hits[0][1], hits[0][2]

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

    def get_intersection_and_normal(self, ray):
        if ray.terminated: return None, None

        # Plane Intersection (Standard math)
        denom = np.dot(ray.dir, self.normal)
        if abs(denom) < 1e-12: return None, None # Parallel to plane
        t = np.dot(self.center - ray.pos, self.normal) / denom
        if t < 1e-9: return None, None # Behind the ray
        
        hit_pos = ray.pos + t * ray.dir
        dist_sq = np.dot(hit_pos - self.center, hit_pos - self.center) # Distance from Center
        
        if dist_sq <= self.radius**2: # Check if it is a miss (pass through)
            return None, None
            
        # If we are OUTSIDE the hole, it is a "Hit" (Ray hits the metal stop)
        # Note: You can add an 'outer_radius' check here too if you want a finite washer
        # but usually apertures are treated as infinite planes.
        if dist_sq > self.outer_radius**2:
            return None, None
        
        return hit_pos, self.normal

    def physics(self, ray, hit_pos, normal_at_hit):

        # If the ray actually "hit" this element, it means it hit the opaque part.
        return ray.dir, True

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

# ==========================================
# Utilities and Functions
# ==========================================

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

def run_simulation(rays, elements, bounces, use_gpu):    
    # elements = sorted(elements, key=lambda e: e.center[0]) # Sort by X to help simple sequential tracing
    
    for ray in rays:
        for _ in range(bounces): # Max bounces
            if ray.terminated: break
            
            closest_el = None
            closest_dist = float('inf')
            closest_normal = None
            
            for el in elements:                
                hit, normal = el.get_intersection_and_normal(ray) # Check intersection
                
                if hit is not None:
                    dist = np.linalg.norm(hit - ray.pos)
                    if dist > 1e-6 and dist < closest_dist:
                        closest_dist = dist
                        closest_el = el
                        closest_normal = normal
            
            if closest_el:
                if closest_normal is None: # The ray gets killed by the prism corner
                    ray.terminated = True
                else:
                    closest_el.interact(ray)
            else:
                ray.update(ray.pos + ray.dir * 0.5) # Infinity, no direction set
                break

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


# ==========================================
# Example Run
# ==========================================


if __name__ == "__main__":
    
    # Elements
    
    # Collimator Lens (Thin/Flat approximation)
    l1 = ThinLens("Collimator", [0.2, 0], [1, 0], 0.1, 0.2)
    
    # Grating (Flat)
    # Tilted 15 degrees
    ang = np.radians(15)
    g_norm = [np.cos(ang), np.sin(ang)]
    grating = TransmissionGrating("Grating", [0.5, 0], [1, 0], 0.1, 600, 2)

    glass = Slab("Nom Nom", [0.5, 0], g_norm, 0.4, "BK7", 0.1)

    l2 = Lens("Fun lens", [0.5, 0], [1, 0], 0.1, "BK7", 0.3, -0.3, 0.0075)
    
    # Spherical Mirror (Curved)
    # Concave mirror focusing light.
    # Radius = 0.5. Normal = [-1, -0.5] (pointing back left-ish)
    m_norm = np.array([-1, -0.5])
    m_norm /= np.linalg.norm(m_norm)
    mirror = FlatMirror("Flat Mirror", [0.6, 0], [1, 0], 0.1)
    
    # Detector (Flat)
    screen = Screen("Detector", [0.18, 0.04], [1, 0], 0.02)

    prism = Prism("AA", [0.5, 0], [0, -1], "BK7", 60, 0.20)

    p_mirror = ParabolicMirror("Focuser", [0.5, 0], [-1, 0], 0.1, 0.2)
    
    aperture = CircularAperture("pinhole", [0.05, 0], [1, 0], 0.02, 0.1)

    elements = [aperture, p_mirror, screen, mirror, glass]
    
    # Source
    waves = [(100, 'blue')]
    rays = generate_point_source(waves, np.array([0,0]), l1.center, l1.aperture*2, 3)
    add = generate_gaussian_beam_deter(waves, [0,0], [1, 0], l1.aperture, 40)
    rays.extend(add)
    
    # Simulate
    run_simulation(add, elements, 15, True)

    # print(rays[0].path)
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_system(rays, elements, ax)
    # screen_result(screen, rays, ax)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title("Mirror inside Glass Slab")
    plt.show()
// Compiling commands I used:
// Linux: g++ -O3 -shared -fPIC -o engine_cpp.so engine_cpp.cpp
// Windows: g++ -shared -o engine_cpp.dll engine_cpp.cpp -O3
// Kindly change the commands as per your requirements.

#include <cmath>
#define edgetol 1e-5f // to prevent leaks
#define intertol 1e-6f // to provide self intersection

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

// --------------------------------------------------------
// Data Structures (Match Python Packing with Padding)
// --------------------------------------------------------

struct Ray {
    // 7 Floats total
    float type_id;      // -1 (Flag for screen detection)
    float active;       // 1 = Active, 0 = Dead
    float wavelength;   
    float x, y;         // Position
    float dx, dy;       // Direction (Normalized)
};

struct Element {
    // 30 Floats total
    
    // Header (Standard for all elements)
    float type;         // 0=Para, 1=Flat, 2=Sphere, etc.
    float id;           // Unique ID
    float cx, cy;       // Center (x, y)
    float nx, ny;       // Normal (x, y)
    float aperture;     // Diameter/Width
    
    // Extra Payload (Context dependent) 
    float params[23];   // Size = 23 floats (Maximum extra parameters for the prism class)
};

// --------------------------------------------------------
// Intersection Logic
// --------------------------------------------------------

// Helper function specific to Thick Lens intersection
float check_lens_surface(const Ray& r, float cc_x, float cc_y, float radius_abs, 
                         float vertex_x, float vertex_y, float aperture, 
                         float lens_nx, float lens_ny, int surface_side, 
                         float& out_nx, float& out_ny) {
    
    // Ray-Sphere Intersection Math (parametric)
    // |O + tD - CC|^2 = R^2
    float Lx = r.x - cc_x;
    float Ly = r.y - cc_y;

    float b = 2.0f * (r.dx * Lx + r.dy * Ly);
    float c = (Lx * Lx + Ly * Ly) - (radius_abs * radius_abs);

    float disc = b * b - 4.0f * c;
    if (disc < 0.0f) return -1.0f;

    float sqrt_disc = std::sqrt(disc);
    float t1 = (-b - sqrt_disc) / 2.0f;
    float t2 = (-b + sqrt_disc) / 2.0f;

    // Setup Aperture/Cap Logic initailisation
    float semi_aperture = (aperture / 2.0f) + edgetol;
    float ratio = semi_aperture / radius_abs;
    if (ratio > 1.0f) ratio = 1.0f; // Aperture capping
    float min_cos_theta = std::sqrt(1.0f - ratio * ratio); // Threshold cosine

    float ax_x = vertex_x - cc_x; // Axis Vector (Center of Curvature -> Vertex)
    float ax_y = vertex_y - cc_y;

    float ax_len = std::sqrt(ax_x*ax_x + ax_y*ax_y);
    if (ax_len > 1e-9f) { ax_x /= ax_len; ax_y /= ax_len; } // Normalize Axis with a check for division by zero

    // Find Closest Valid Hit
    float min_t = 1e30f;
    bool valid_hit = false;
    float final_hit_x = 0.0f;
    float final_hit_y = 0.0f;

    float candidates[2] = {t1, t2};

    for (int i = 0; i < 2; i++) {
        float t = candidates[i];
        if (t > intertol && t < min_t) {
            float hx = r.x + r.dx * t;
            float hy = r.y + r.dy * t;

            float hit_vec_x = hx - cc_x; // Vector from CC to Hit
            float hit_vec_y = hy - cc_y;
            
            float hv_x = hit_vec_x / radius_abs;// Normalize (divide by radius)
            float hv_y = hit_vec_y / radius_abs;

            float cos_theta = ax_x * hv_x + ax_y * hv_y; // Dot product with Axis

            if (cos_theta >= min_cos_theta) { // The Conditional check for physically valid intersections
                min_t = t;
                final_hit_x = hx;
                final_hit_y = hy;
                valid_hit = true;
            }
        }
    }

    if (!valid_hit) return -1.0f; // No physically valid intersections

    // Geometric Normal Calculation
    float n_raw_x = final_hit_x - cc_x; // Raw normal (the sign might be inverted for now) 
    float n_raw_y = final_hit_y - cc_y;
    
    float n_len = std::sqrt(n_raw_x*n_raw_x + n_raw_y*n_raw_y); // Normalize
    if (n_len > 1e-9f) { n_raw_x /= n_len; n_raw_y /= n_len; }
    
    float proj = n_raw_x * lens_nx + n_raw_y * lens_ny;

    if ((surface_side == -1 && proj > 0.0f) || (surface_side == 1 && proj < 0.0f)) { 
        // If surface is Left (-1) and proj is positive, n_raw is pointing wrong. Flip.
        // If surface is Right (+1) and proj is negative, n_raw is pointing wrong. Flip.
        out_nx = -n_raw_x;
        out_ny = -n_raw_y;
    } else {
        out_nx = n_raw_x;
        out_ny = n_raw_y;
    }

    return min_t;
}

// Helper function specific to Prism face interaction
float check_prism_face(const Ray& r, float p1_x, float p1_y, float p2_x, float p2_y, 
                       float face_nx, float face_ny, float& out_nx, float& out_ny, int& kill_flag) {
    
    // Standard Ray-Plane Intersection (parametric)
    // t = ((P1 - Origin) . Normal) / Denom
    float denom = r.dx * face_nx + r.dy * face_ny;
    if (std::abs(denom) < 1e-9f) return -1.0f; // Check Parallel
    float vec_x = p1_x - r.x;
    float vec_y = p1_y - r.y;
    float t = (vec_x * face_nx + vec_y * face_ny) / denom;

    if (t < intertol) return -1.0f; // Check Behind

    // Finite Segment Check (Aperture check)  
    float hx = r.x + r.dx * t; // Calculate Hit Point
    float hy = r.y + r.dy * t;
    float edge_x = p2_x - p1_x; 
    float edge_y = p2_y - p1_y; 
    float hit_vec_x = hx - p1_x; 
    float hit_vec_y = hy - p1_y;

    float proj = hit_vec_x * edge_x + hit_vec_y * edge_y; // Project Hit onto Edge (Dot Product)
    float edge_len_sq = edge_x * edge_x + edge_y * edge_y;
    float edge_len = std::sqrt(edge_len_sq);

    float kill_zone = 1e-4f;
    float clip_val = kill_zone * edge_len; // Scale by edge length

    if (proj >= 0.0f - (edgetol * edge_len) && proj <= edge_len_sq + (edgetol * edge_len)) { // The condition check
        // Valid Hit
        if (proj < clip_val || proj > (edge_len_sq - clip_val)) { // Check if the hit is too close to the edge
            kill_flag = 1; // Mark fatal
        }
        out_nx = face_nx;
        out_ny = face_ny;
        return t;
    }
    return -1.0f;
}

float intersect_parabolic(const Ray& r, const Element& el, float& out_nx, float& out_ny) {

    // Unpack the parameters
    float fx = el.params[0]; // Focal Length
    float R_wtl_00 = el.params[6];
    float R_wtl_01 = el.params[7];
    float R_wtl_10 = el.params[8];
    float R_wtl_11 = el.params[9];
    float R_ltw_00 = el.params[10];
    float R_ltw_01 = el.params[11];
    float R_ltw_10 = el.params[12];
    float R_ltw_11 = el.params[13];

    // Transform ray to the local system
    float rel_x = r.x - el.cx; // Relative Position (Ray - Center)
    float rel_y = r.y - el.cy;

    float ux = R_wtl_00 * rel_x + R_wtl_01 * rel_y; // Apply Rotation (Matrix * Vector) to find local coordinates and local directions
    float uy = R_wtl_10 * rel_x + R_wtl_11 * rel_y;
    float dx = R_wtl_00 * r.dx + R_wtl_01 * r.dy;
    float dy = R_wtl_10 * r.dx + R_wtl_11 * r.dy;

    // Solve the quadratic equation for the parametric intersection
    // (uy + t*dy)^2 = 4*f*(ux + t*dx) => A*t^2 + B*t + C = 0
    float A = dy * dy;
    float B = 2.0f * uy * dy - 4.0f * fx * dx;
    float C = uy * uy - 4.0f * fx * ux;

    float t1 = -1.0f;
    float t2 = -1.0f;
  
    if (std::abs(A) < 1e-9f) { // Check for linear case
        if (std::abs(B) > 1e-9f) {
            t1 = -C / B;
        } else { // A=0 AND B=0: Impossible for valid rays.
        return -1.0f; // Treat as no intersection to prevent NaN/Infinity.
        }
    } else {
        float discriminant = B * B - 4.0f * A * C;
        if (discriminant >= 0.0f) { // Intersection check for the general parabola
            float sqrt_disc = std::sqrt(discriminant);
            t1 = (-B - sqrt_disc) / (2.0f * A);
            t2 = (-B + sqrt_disc) / (2.0f * A);
        }
    }

    // Check positive t and Aperture
    float min_t = 1e30f;
    bool hit_found = false;
    float candidates[2] = {t1, t2};

    float final_local_u = 0.0f; // To store hit u for normal calc
    float final_local_v = 0.0f; // To store hit v for normal calc

    for (int i = 0; i < 2; i++) {
        float t = candidates[i];
        if (t > intertol && t < min_t) { // 1e-6 epsilon to prevent intersection with the element again            
            float hit_v = uy + t * dy; // Calculate Hit Height in Local Frame (v)             
            if (std::abs(hit_v) <= (el.aperture / 2.0f) + edgetol ) { // Check Aperture
                min_t = t;
                final_local_u = ux + t * dx;
                final_local_v = hit_v;
                hit_found = true;
            }
        }
    }

    if (!hit_found) return -1.0f; // No physically viable hits

    // Normal calculation
    float local_nx = -4.0f * fx;
    float local_ny = 2.0f * final_local_v;
    out_nx = R_ltw_00 * local_nx + R_ltw_01 * local_ny; // Transform Normal back to World Space (R_local_to_world)
    out_ny = R_ltw_10 * local_nx + R_ltw_11 * local_ny;
    float len = std::sqrt(out_nx*out_nx + out_ny*out_ny);
    if (len > 1e-9f) { // Normalize after checking for division by zero
        out_nx /= len;
        out_ny /= len;
    }

    float dot = out_nx * r.dx + out_ny * r.dy;
    if (dot > 0.0f) { // Ensure Normal points against the Ray
        out_nx = -out_nx;
        out_ny = -out_ny;
    }

    return min_t;
}

float intersect_flat(const Ray& r, const Element& el, float& out_nx, float& out_ny) {
    
    // Parametric intersection formula
    // t = ((C - O) . N) / (D . N)
    float denom = r.dx * el.nx + r.dy * el.ny;
    if (std::abs(denom) < 1e-9f) return -1.0f; // Check for parallellism
    float vec_x = el.cx - r.x;
    float vec_y = el.cy - r.y;
    float numer = vec_x * el.nx + vec_y * el.ny;
    float t = numer / denom;
    if (t < intertol) return -1.0f; // Check if the element is in front of the ray

    // Check aperture
    float hit_x = r.x + r.dx * t;
    float hit_y = r.y + r.dy * t;
    float rel_hit_x = hit_x - el.cx;
    float rel_hit_y = hit_y - el.cy;
    float tx = -el.ny; // Tangent is Normal rotated 90 deg anticlockwise
    float ty =  el.nx;
    float local_height = rel_hit_x * tx + rel_hit_y * ty; // Calculate the local height (dot product)
    if (std::abs(local_height) > (el.aperture / 2.0f) + edgetol) { // Check the aperture
        return -1.0f;
    }
    
    // The normals stay the same for a flatt surface
    out_nx = el.nx;
    out_ny = el.ny;

    return t;
}

float intersect_spherical(const Ray& r, const Element& el, float& out_nx, float& out_ny) {
    
    // Unpack the parameters
    float radius_val = el.params[0];
    float cc_x       = el.params[1];
    float cc_y       = el.params[2];
    float r_abs = std::abs(radius_val);

    // Parametric sphere intersection calculation
    // |O + tD - CC|^2 = R^2
    float Lx = r.x - cc_x;
    float Ly = r.y - cc_y;
    float b = 2.0f * (r.dx * Lx + r.dy * Ly);
    float c = (Lx * Lx + Ly * Ly) - (r_abs * r_abs);
    float discriminant = b * b - 4.0f * c;
    if (discriminant < 0.0f) return -1.0f; // Missed sphere entirely
    float sqrt_disc = std::sqrt(discriminant);
    float t1 = (-b - sqrt_disc) / 2.0f;
    float t2 = (-b + sqrt_disc) / 2.0f;

    // Cosine threshold calculation for aperture check
    float semi_aperture = (el.aperture / 2.0f) + edgetol;
    float ratio = semi_aperture / r_abs;
    if (ratio > 1.0f) ratio = 1.0f; // Clamp for safety
    float min_cos_theta = std::sqrt(1.0f - ratio * ratio);

    float ax_x = el.cx - cc_x; // Calculation of the reference axis
    float ax_y = el.cy - cc_y;
    float ax_len = std::sqrt(ax_x*ax_x + ax_y*ax_y); 
    if (ax_len > 1e-9f) { ax_x /= ax_len; ax_y /= ax_len; } // Normalize after the check for zero division

    // Check for the physically valid nearest hit
    float candidates[2] = {t1, t2};
    float min_t = 1e30f;
    bool found_valid = false;

    float final_hit_x = 0.0f;
    float final_hit_y = 0.0f;

    for (int i = 0; i < 2; i++) {
        float t = candidates[i];
        
        if (t > intertol && t < min_t) { // Check if the element is in front of the ray
            float hx = r.x + r.dx * t;
            float hy = r.y + r.dy * t;

            float hit_vec_x = hx - cc_x;
            float hit_vec_y = hy - cc_y;

            float hv_x = hit_vec_x / r_abs; // Normalize
            float hv_y = hit_vec_y / r_abs;

            float cos_theta = ax_x * hv_x + ax_y * hv_y;

            if (cos_theta >= min_cos_theta) { // Cosine check 
                min_t = t;
                final_hit_x = hx;
                final_hit_y = hy;
                found_valid = true;
            }
        }
    }

    if (!found_valid) return -1.0f; // No physically valid intersections

    // Calculate normal
    out_nx = final_hit_x - cc_x;
    out_ny = final_hit_y - cc_y;
    
    float n_len = std::sqrt(out_nx*out_nx + out_ny*out_ny);
    if (n_len > 1e-9f) { // Normalize
        out_nx /= n_len;
        out_ny /= n_len;
    }

    float dot_dir = out_nx * r.dx + out_ny * r.dy;
    if (dot_dir > 0.0f) { // Flip normal if it points same direction as Ray
        out_nx = -out_nx;
        out_ny = -out_ny;
    }

    return min_t;
}

float intersect_slab(const Ray& r, const Element& el, float& out_nx, float& out_ny) {

    // Unpack the parameters
    float c1_x = el.params[1];
    float c1_y = el.params[2];
    float n1_x = el.params[3];
    float n1_y = el.params[4];
    float c2_x = el.params[5];
    float c2_y = el.params[6];
    float n2_x = el.params[7];
    float n2_y = el.params[8];
    float tx = -el.ny; // The tangesnt is found by rotating the normal by 90 deg anticlockwise
    float ty =  el.nx;

    // Check both faces for valid intersections
    float min_t = 1e30f;
    bool hit_found = false;

    float denom1 = r.dx * n1_x + r.dy * n1_y; // Face 1
    
    if (std::abs(denom1) > 1e-9f) { // Parallel check (denom close to 0)
        float vec_x = c1_x - r.x;
        float vec_y = c1_y - r.y;
        
        float t = (vec_x * n1_x + vec_y * n1_y) / denom1;

        if (t > intertol) { // Forward check (t > epsilon)
            float hx = r.x + r.dx * t;
            float hy = r.y + r.dy * t;
            float rel_x = hx - c1_x;
            float rel_y = hy - c1_y;
            float h = rel_x * tx + rel_y * ty;

            if (std::abs(h) <= (el.aperture / 2.0f) + edgetol) { // Aperture Check
                if (t < min_t) {
                    min_t = t;
                    out_nx = n1_x;
                    out_ny = n1_y;
                    hit_found = true;
                }
            }
        }
    }

    float denom2 = r.dx * n2_x + r.dy * n2_y; // Face 2 (Same as the above calculation)
    
    if (std::abs(denom2) > 1e-12f) {
        float vec_x = c2_x - r.x;
        float vec_y = c2_y - r.y;
        
        float t = (vec_x * n2_x + vec_y * n2_y) / denom2;

        if (t > intertol) {
            if (t < min_t) { // Optimisation (Calculations done only when the hit is nearer)
                float hx = r.x + r.dx * t;
                float hy = r.y + r.dy * t;
                
                float rel_x = hx - c2_x;
                float rel_y = hy - c2_y;

                float h = rel_x * tx + rel_y * ty;

                if (std::abs(h) <= (el.aperture / 2.0f) + edgetol) {
                    min_t = t;
                    out_nx = n2_x;
                    out_ny = n2_y;
                    hit_found = true;
                }
            }
        }
    }

    if (!hit_found) return -1.0f; // No physically viable hits

    return min_t;
}

float intersect_thick_lens(const Ray& r, const Element& el, float& out_nx, float& out_ny) {
    
    // Unpack the Parameters
    float R1_abs = std::abs(el.params[1]);
    float R2_abs = std::abs(el.params[2]);
    
    float v1_x = el.params[3];
    float v1_y = el.params[4];
    float v2_x = el.params[5];
    float v2_y = el.params[6];

    float cc1_x = el.params[7];
    float cc1_y = el.params[8];
    float cc2_x = el.params[9];
    float cc2_y = el.params[10];

    float lens_nx = el.nx; // Lens Axis (Normal) for orientation checks
    float lens_ny = el.ny;

    // Check Surface 1 (Front): Side -1
    float nx1 = 0, ny1 = 0;
    float t1 = check_lens_surface(r, cc1_x, cc1_y, R1_abs, v1_x, v1_y, el.aperture, 
                                  lens_nx, lens_ny, -1, nx1, ny1);

    // Check Surface 2 (Back): Side 1
    float nx2 = 0, ny2 = 0;
    float t2 = check_lens_surface(r, cc2_x, cc2_y, R2_abs, v2_x, v2_y, el.aperture, 
                                  lens_nx, lens_ny, 1, nx2, ny2);

    // Return Closest Hit
    if (t1 < 0.0f && t2 < 0.0f) return -1.0f; // Missed both

    if (t1 > 0.0f) {
        if (t2 > 0.0f) { // Both hit, pick closer
            if (t1 < t2) {
                out_nx = nx1; out_ny = ny1; return t1;
            } else {
                out_nx = nx2; out_ny = ny2; return t2;
            }
        } else { // Only t1 hit
            out_nx = nx1; out_ny = ny1; return t1;
        }
    } else { // Only t2 hit (t1 missed)
        out_nx = nx2; out_ny = ny2; return t2;
    }
}

float intersect_prism(const Ray& r, const Element& el, float& out_nx, float& out_ny, int& kill_flag) {

    // Unpack the Parameters 
    float p_apex_x = el.params[4];
    float p_apex_y = el.params[5];
    float p_top_x = el.params[6];
    float p_top_y = el.params[7];
    float p_bot_x = el.params[8];
    float p_bot_y = el.params[9];

    float n_base_x = el.params[10];
    float n_base_y = el.params[11];
    float n_top_x = el.params[12];
    float n_top_y = el.params[13];
    float n_bot_x = el.params[14];
    float n_bot_y = el.params[15];

    // Check All 3 Faces
    float min_t = 1e30f;
    bool hit_found = false;

    float tx, ty; // Temp variables for normals
    float t;

    kill_flag = 0;

    int k1 = 0;
    t = check_prism_face(r, p_apex_x, p_apex_y, p_top_x, p_top_y, n_top_x, n_top_y, tx, ty, k1); // Face 1
    if (t > 0.0f && t < min_t) {
        min_t = t;
        out_nx = tx; out_ny = ty;
        kill_flag = k1;
        hit_found = true;
    }

    int k2 = 0;
    t = check_prism_face(r, p_bot_x, p_bot_y, p_apex_x, p_apex_y, n_bot_x, n_bot_y, tx, ty, k2); // Face 2
    if (t > 0.0f && t < min_t) {
        min_t = t;
        out_nx = tx; out_ny = ty;
        kill_flag = k2;
        hit_found = true;
    }

    int k3 = 0;
    t = check_prism_face(r, p_top_x, p_top_y, p_bot_x, p_bot_y, n_base_x, n_base_y, tx, ty, k3); // Face 3
    if (t > 0.0f && t < min_t) {
        min_t = t;
        out_nx = tx; out_ny = ty;
        kill_flag = k3;
        hit_found = true;
    }

    if (!hit_found) return -1.0f; // No physically viable hits

    return min_t;
}

float intersect_aperture(const Ray& r, const Element& el, float& out_nx, float& out_ny) {

    // Unpack the Parameters
    float hole_radius = el.params[0] - edgetol;
    float outer_radius = el.params[1] + edgetol; 

    // Parametric plane intersection
    float denom = r.dx * el.nx + r.dy * el.ny;

    if (std::abs(denom) < 1e-12f) return -1.0f; // Parallel check

    float vec_x = el.cx - r.x;
    float vec_y = el.cy - r.y;
    float t = (vec_x * el.nx + vec_y * el.ny) / denom; // Calculate t

    if (t < intertol) return -1.0f; // Behind check

    // Aperture Check
    float hit_x = r.x + r.dx * t;
    float hit_y = r.y + r.dy * t;

    float dx = hit_x - el.cx;
    float dy = hit_y - el.cy;
    float dist_sq = dx*dx + dy*dy; // Distance squared from center

    if (dist_sq <= hole_radius * hole_radius) {
        return -1.0f; // Passed through the hole
    }
    if (dist_sq > outer_radius * outer_radius) {
        return -1.0f; // Completely missed the aperture walls
    }

    // No changes to the normal
    out_nx = el.nx;
    out_ny = el.ny;

    return t;
}

// --------------------------------------------------------
// Optical Physics
// --------------------------------------------------------

// Helper Function to Calculate Refractive Index from Sellmeier or Fixed value
float get_index(const Element& el, int offset, float wav_nm) {
    float rcase = el.params[offset]; // 1=Fixed, 2=Sellmeier

    if (rcase == 1.0f) {
        return el.params[offset + 1];
    } else { // Sellmeier Coefficients
        float L = wav_nm / 1000.0f; // microns
        float L2 = L * L;
        
        float B1 = el.params[offset+1]; float B2 = el.params[offset+2]; float B3 = el.params[offset+3];
        float C1 = el.params[offset+4]; float C2 = el.params[offset+5]; float C3 = el.params[offset+6];

        float n2 = 1.0f + (B1 * L2)/(L2 - C1) + (B2 * L2)/(L2 - C2) + (B3 * L2)/(L2 - C3);
        return std::sqrt(n2);
    }
}

// Helper Function to Apply Snell's Law (Refraction)
void apply_refraction(Ray& r, float nx, float ny, float n_glass) {
    float dot = r.dx * nx + r.dy * ny;
    float n1 = 1.0f;     // Air
    float n2 = n_glass;  // Material
    float normal_x = nx;
    float normal_y = ny;

    // Check whether we are entering or exiting
    if (dot < 0.0f) { // Entering (Normal is correct)
    } else { // Exiting (Flip normal, swap indices)
        n1 = n_glass;
        n2 = 1.0f;
        normal_x = -nx;
        normal_y = -ny;
        dot = -dot;
    }

    float eta = n1 / n2; // Relative indices
    float k = 1.0f - eta * eta * (1.0f - dot * dot);

    if (k < 0.0f) { // Check for TIR, in which case, the ray gets reflected
        r.dx = r.dx - 2.0f * dot * normal_x;
        r.dy = r.dy - 2.0f * dot * normal_y;
    } else { // Refract
        float term = eta * dot + std::sqrt(k);
        r.dx = eta * r.dx - term * normal_x;
        r.dy = eta * r.dy - term * normal_y;
    }
    
    float len = std::sqrt(r.dx*r.dx + r.dy*r.dy); 
    if (len > 1e-9f) { // Normalize
        r.dx /= len; 
        r.dy /= len;
    }
}

void interact_parabolic(Ray& r, const Element& el, float nx, float ny) {

    // Reflection: R = D - 2(D.N)N
    float dot = r.dx * nx + r.dy * ny;
    
    r.dx = r.dx - 2.0f * dot * nx;
    r.dy = r.dy - 2.0f * dot * ny;
}

void interact_flat_mirror(Ray& r, const Element& el, float nx, float ny) {

    // Reflection math
    float dot = r.dx * nx + r.dy * ny;
    
    r.dx = r.dx - 2.0f * dot * nx;
    r.dy = r.dy - 2.0f * dot * ny;
}

void interact_spherical_mirror(Ray& r, const Element& el, float nx, float ny) {

    // Reflection math
    float dot = r.dx * nx + r.dy * ny;
    
    r.dx = r.dx - 2.0f * dot * nx;
    r.dy = r.dy - 2.0f * dot * ny;
}

void interact_screen(Ray& r, const Element& el, float nx, float ny) {

    // Ray is absorbed/detected
    r.active = 0.0f; 
    r.type_id = el.id;
}

void interact_aperture(Ray& r, const Element& el, float nx, float ny) {

    // If we are here, we hit the walls and the ray is absorbed
    r.active = 0.0f;
}

void interact_slab(Ray& r, const Element& el, float nx, float ny) {

    // Use helper functions for refraction physics
    float n = get_index(el, 9, r.wavelength);
    apply_refraction(r, nx, ny, n);
}

void interact_thick_lens(Ray& r, const Element& el, float nx, float ny) {
    
    // Use helper functions for refraction physics
    float n = get_index(el, 11, r.wavelength);
    apply_refraction(r, nx, ny, n);
}

void interact_prism(Ray& r, const Element& el, float nx, float ny) {
    
    // Use helper functions for refraction physics
    float n = get_index(el, 16, r.wavelength);
    apply_refraction(r, nx, ny, n);
}

void interact_thin_lens(Ray& r, const Element& el, float nx, float ny) {
    float f = el.params[0]; // Focal Length

    float vec_hit_x = r.x - el.cx;
    float vec_hit_y = r.y - el.cy;

    float tx = -ny; // Calculate the tangent by rotating the normal by 90 deg anticlockwise
    float ty = nx;
    float h = vec_hit_x * tx + vec_hit_y * ty; // Calculate Signed Height (Project Hit Vector onto Tangent)

    // Calculate Deflection Angle (delta) = height / self.focal_length
    float delta = h / f;
    float dot_prod = r.dx * nx + r.dy * ny;
    if (dot_prod < 0.0f) { // Directional check
        delta = -delta;
    }

    // Calculate the final ray direction
    float theta = -delta;
    float c = std::cos(theta);
    float s = std::sin(theta);

    float new_dx = c * r.dx - s * r.dy;
    float new_dy = s * r.dx + c * r.dy;

    r.dx = new_dx;
    r.dy = new_dy;

    float len = std::sqrt(r.dx*r.dx + r.dy*r.dy);
    if (len > 1e-9f) { // Normalize
        r.dx /= len;
        r.dy /= len;
    }
}

void interact_trans_grating(Ray& r, const Element& el, float nx, float ny) {

    // Unpack the Parameters
    float order = el.params[1];
    float d     = el.params[0];

    float tx = -ny; // Calculate the tangent by rotating the normal by 90 deg anticlockwise
    float ty =  nx;

    // Determine the Corrected Normal
    float cos_i = r.dx * nx + r.dy * ny;
    float sin_i = r.dx * tx + r.dy * ty;

    float c_nx = nx;
    float c_ny = ny;
    if (cos_i < 0.0f) { // For transmission, we  want the normal pointing WITH the ray (Forward)
        c_nx = -nx;
        c_ny = -ny;
    }

    // Grating Equation: sin(theta_m) = sin(theta_i) + m * lambda / d
    float term = (order * r.wavelength * 1e-9f) / d;
    float sin_m = sin_i + term;

    // Evanescent Check (Absorb if invalid)
    if (std::abs(sin_m) > 1.0f) {
        r.active = 0.0f;
        return;
    }

    // Construct Outgoing Vector
    float theta_m = std::asin(sin_m);
    float cos_theta_m = std::cos(theta_m);

    r.dx = cos_theta_m * c_nx + sin_m * tx; // u = cos(theta_m) * N_corr + sin(theta_m) * T
    r.dy = cos_theta_m * c_ny + sin_m * ty;

    float len = std::sqrt(r.dx*r.dx + r.dy*r.dy);
    if (len > 1e-9f) { // Normalize
        r.dx /= len;
        r.dy /= len;
    }
}

void interact_refl_grating(Ray& r, const Element& el, float nx, float ny) {

    // Unpack the Parameters
    float d = el.params[0];
    float order        = el.params[1];

    float tx = -ny; // Calculate the tangent by rotating the normal by 90 deg anticlockwise
    float ty =  nx;

    // Determine the Corrected Normal
    float cos_i = r.dx * nx + r.dy * ny;
    float sin_i = r.dx * tx + r.dy * ty;

    float c_nx = nx;
    float c_ny = ny;
    if (cos_i >= 0.0f) { // For reflection, we  want the normal pointing against the ray (Backward)
        c_nx = -nx;
        c_ny = -ny;
    }

    // Grating Equation: sin(theta_m) = sin(theta_i) + m * lambda / d
    float term = (order * r.wavelength * 1e-9f) / d;
    float sin_m = sin_i + term;

    // Evanescent Check (Absorb if invalid)
    if (std::abs(sin_m) > 1.0f) {
        r.active = 0.0f;
        return;
    }

    // Construct Outgoing Vector
    float theta_m = std::asin(sin_m);
    float cos_theta_m = std::cos(theta_m);

    r.dx = cos_theta_m * c_nx + sin_m * tx; // u = cos(theta_m) * N_corr + sin(theta_m) * T
    r.dy = cos_theta_m * c_ny + sin_m * ty;

    float len = std::sqrt(r.dx*r.dx + r.dy*r.dy);
    if (len > 1e-9f) { // Normalize
        r.dx /= len;
        r.dy /= len;
    }
}

// --------------------------------------------------------
// The Simulation Kernel
// --------------------------------------------------------

extern "C" {

// This function receives raw memory pointers from Python/NumPy
EXPORT void simulate_c(float* raw_ray_ptr, int num_rays, 
                    float* raw_element_ptr, int num_elements, int rounds, float* interaction_ptr, float* record_ptr) {// interaction array should have 2 * no. of rays * (no. of rounds + 1) elements initialised to -inf

    // Cast to discrete rays and elements 
    Ray* rays = reinterpret_cast<Ray*>(raw_ray_ptr);
    Element* elements = reinterpret_cast<Element*>(raw_element_ptr);

    // The Simulation loop
    for (int i = 0; i < num_rays; i++) {
        Ray& r = rays[i];
        int i_index = i * 2 * (rounds +1);
        interaction_ptr[i_index] = r.x;
        interaction_ptr[i_index + 1] = r.y;

        // The bounce loop
        for (int j = 0; j < rounds; j++) {
            if (std::abs(r.dx) < 1e-4f && std::abs(r.dy) < 1e-4f) { // Kill the ray if its direction vector is 0
                r.active = 0.0f;
            }
            if (r.active == 0.0f) break;

            // Initialise variables
            float min_dist = 1e30f; 
            int hit_idx = -1; // Not yet hit
            float closest_nx = 0.0f; // To Store the normal vector of the closest hit
            float closest_ny = 0.0f;
            float tmp_nx = 0.0f; // Temp variables for the current check
            float tmp_ny = 0.0f;
            int round_kill = 0;

            // Find the nearest object
            for (int k = 0; k < num_elements; k++) {
                Element& el = elements[k];
                int current_kill = 0;
                float d = -1.0f;

                switch ((int)el.type) { // 11-Fold Switch for intersection (Geometry)
                    case 0: d = intersect_parabolic(r, el, tmp_nx, tmp_ny); break;
                    case 1: d = intersect_flat(r, el, tmp_nx, tmp_ny); break;      // Flat Mirror
                    case 2: d = intersect_spherical(r, el, tmp_nx, tmp_ny); break; // Spherical Mirror
                    case 3: d = intersect_flat(r, el, tmp_nx, tmp_ny); break;      // Screen
                    case 4: d = intersect_flat(r, el, tmp_nx, tmp_ny); break;      // Thin Lens
                    case 5: d = intersect_flat(r, el, tmp_nx, tmp_ny); break;      // Trans Grating
                    case 6: d = intersect_flat(r, el, tmp_nx, tmp_ny); break;      // Refl Grating
                    case 7: d = intersect_slab(r, el, tmp_nx, tmp_ny); break;      // Slab
                    case 8: d = intersect_thick_lens(r, el, tmp_nx, tmp_ny); break;// Thick Lens
                    case 9: d = intersect_prism(r, el, tmp_nx, tmp_ny, current_kill); break;     // Prism
                    case 10: d = intersect_aperture(r, el, tmp_nx, tmp_ny); break; // Aperture
                }

                if (d > intertol && d < min_dist) { // Keep the closest valid hit (0.001f prevents self-intersection errors)
                    closest_nx = tmp_nx;
                    closest_ny = tmp_ny;
                    min_dist = d;
                    hit_idx = k;
                    round_kill = current_kill;
                }
            }

            int j_index = i_index + (j + 1) * 2;

            if (hit_idx != -1 && round_kill == 1) {
                // Move ray to the edge for visual clarity and then kill it
                r.x += r.dx * min_dist; 
                r.y += r.dy * min_dist;
                
                int j_index = i_index + (j + 1) * 2;
                interaction_ptr[j_index] = r.x;
                interaction_ptr[j_index + 1] = r.y;
                
                r.active = 0.0f;
                break; 
            }

            // Apply Physics
            if (hit_idx != -1) {
                Element& target = elements[hit_idx];

                r.x += r.dx * min_dist; // Move Ray to the hit point
                r.y += r.dy * min_dist;
 
                interaction_ptr[j_index] = r.x;
                interaction_ptr[j_index + 1] = r.y;
                
                switch ((int)target.type) { // Call Physics Functions
                    case 0: interact_parabolic(r, target, closest_nx, closest_ny); break;
                    case 1: interact_flat_mirror(r, target, closest_nx, closest_ny); break;
                    case 2: interact_spherical_mirror(r, target, closest_nx, closest_ny); break;
                    case 3: interact_screen(r, target, closest_nx, closest_ny); break;
                    case 4: interact_thin_lens(r, target, closest_nx, closest_ny); break;
                    case 5: interact_trans_grating(r, target, closest_nx, closest_ny); break;
                    case 6: interact_refl_grating(r, target, closest_nx, closest_ny); break;
                    case 7: interact_slab(r, target, closest_nx, closest_ny); break;
                    case 8: interact_thick_lens(r, target, closest_nx, closest_ny); break;
                    case 9: interact_prism(r, target, closest_nx, closest_ny); break;
                    case 10: interact_aperture(r, target, closest_nx, closest_ny); break;
                }
            } else { // Ray hits nothing: It flies off into infinity
                interaction_ptr[j_index] = r.x + 0.5 * r.dx;
                interaction_ptr[j_index + 1] = r.y + 0.5 * r.dy;
                r.active = 0.0f;
            }
        }
        record_ptr[i] = r.type_id;
    }
}
}
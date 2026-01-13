import numpy as np
from scipy.interpolate import PchipInterpolator

def lightDistribution(theta):
    """
    The luminous intensity distribution of our Vivia 7DR3-RGB fixture.
    
    Args:
        theta: angle to normal direction (in radians)
        
    Returns:
        Iq: luminous intensity
    """
    a = np.arange(0, 95, 5) # 0 to 90 inclusive
    I = np.array([509, 505, 456, 398, 333, 269, 203, 142, 91, 49, 15, 1, 0, 0, 0, 0, 0, 0, 0])
    
    # Octave's interp1 with 'pchip' is PchipInterpolator in scipy
    interpolator = PchipInterpolator(a, I)
    
    theta_deg = theta * 180 / np.pi
    return interpolator(theta_deg)

def getReflectionKernel(light, sensor, dim, para):
    """
    Compute the reflection kernel for one sensor-fixture pair.
    
    Args:
        light: 3D spatial coordinates of the light fixture [x, y, z]
        sensor: 3D spatial coordinates of the sensor [x, y, z]
        dim: 3D dimension of the room [dim_x, dim_y, dim_z]
        para: Reflection model parameter (0: non-Lambertian, 1: Lambertian)
        
    Returns:
        K: The resulting reflection kernel (2D matrix of size dim[0] x dim[1])
    """
    lx, ly, lz = light
    sx, sy, sz = sensor
    
    # 1. coordinate grid generation
    # Note: MATLAB/Octave uses 1-based indexing for ndgrid(1:dim(1), 1:dim(2))
    # Python uses 0-based. But the physical coordinates in COSBOS seem to align with indices.
    # To match MATLAB exactly:
    x_range = np.arange(1, dim[0] + 1)
    y_range = np.arange(1, dim[1] + 1)
    
    # Use 'ij' indexing to match ndgrid behavior (matrix encoding)
    X, Y = np.meshgrid(x_range, y_range, indexing='ij')
    
    # 2. Distance calculations
    d1 = np.sqrt((lx - X)**2 + (ly - Y)**2)
    d2 = np.sqrt((sx - X)**2 + (sy - Y)**2)
    
    # 3. 3D Distance calculations
    D1 = np.sqrt(d1**2 + lz**2)
    D2 = np.sqrt(d2**2 + sz**2)
    
    # 4. Cosine calculations
    cos1 = lz / D1
    cos2 = sz / D2
    
    # 5. Angle calculations
    theta1 = np.arccos(cos1)
    
    # 6. Luminous Intensity calculation
    Iq = lightDistribution(theta1)
    
    # 7. Final Kernel calculation
    v = Iq * cos1 * cos2 / (D1**2) / (D2**2)
    
    # 8. Lambertian correction
    if para == 1:
        v = v * cos2
        
    return v

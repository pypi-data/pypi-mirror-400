import numpy as np

def pointToLineDistance(x, y, z, x1, y1, z1, x2, y2, z2):
    """
    Vectorized calculation of distance from points (x,y,z) to line segments.
    x, y, z can be arrays (broadcast against each other).
    x1...z2 are scalars (or arrays broadcasts against each other).
    
    Returns: distances squared (to avoid sqrt) or distances?
    The C++ implementation returns distances.
    """
    x3 = x2 - x1
    y3 = y2 - y1
    z3 = z2 - z1
    
    segmentLenSq = x3**2 + y3**2 + z3**2
    
    # Avoid division by zero
    # If segmentLenSq is 0, just distance to point 1
    # We can handle this by using where
    
    # Vectorized alpha calculation
    # alpha = ((x - x1) * x3 + (y - y1) * y3 + (z - z1) * z3) / segmentLenSq
    
    # We need to execute this across all voxels AND all lines.
    # Let's say voxels are shape (D,), lines are shape (L,)
    # We can reshape x to (D, 1) and x1 to (1, L).
    pass 

def hashGaussians(sensors, lights, dim, sigma):
    """
    Python implementation of hashGaussians.cpp
    
    Args:
        sensors: [N, 3] coordinates
        lights: [M, 3] coordinates
        dim: [dim_x, dim_y, dim_z]
        sigma: scalar
        
    Returns:
        H: [prod(dim) * N * M] flat array
    """
    ns = sensors.shape[0]
    nl = lights.shape[0]
    
    # 1. Generate voxel coordinates
    # C++ loop order:
    # for i = 0 to dimProd
    #   x = i % dim[0]
    #   y = (i / dim[0]) % dim[1]
    #   z = i / (dim[0] * dim[1])
    # This corresponds to 'F' (Fortran) order flattening if we had [dim_x, dim_y, dim_z]
    # ACTUALLY:
    # x is inner-most in C++ loop logic above IF a=i is constructed that way
    # Wait, the C++ code says:
    # int x = a % dim[0]; a /= dim[0];
    # int y = a % dim[1]; 
    # int z = a / dim[1];
    # This means x changes fastest. This is consistent with Fortran order (column-major)
    # in a 3D array arr[x, y, z].
    
    nx, ny, nz = int(dim[0]), int(dim[1]), int(dim[2])
    
    # Create grid. Using 'ij' means x varies with first index, which is what we want?
    # np.meshgrid with 'ij' gives X[i,j,k] = i.
    # If we flatten 'F', x changes fastest.
    grid_x, grid_y, grid_z = np.meshgrid(
        np.arange(nx), np.arange(ny), np.arange(nz), indexing='ij'
    )
    
    # Flatten to list of points
    # shape: [num_voxels]
    pts_x = grid_x.flatten('F')
    pts_y = grid_y.flatten('F')
    pts_z = grid_z.flatten('F')
    
    num_voxels = pts_x.shape[0]
    
    # 2. Prepare line segments
    # The C++ loop iterates j over ns*nl
    # s = j % ns; l = j / ns;
    # So s changes fastest.
    # This corresponds to repeating sensors nl times and tiling lights ns times?
    # No.
    # j=0: s=0, l=0
    # j=1: s=1, l=0
    # ...
    # j=ns: s=0, l=1
    
    # Sensors: repeat nl times (outer loop is l)
    # Lights: repeat each element ns times (inner loop is s)
    # Actually, let's just make arrays of shape [ns*nl]
    
    s_idx = np.tile(np.arange(ns), nl)
    l_idx = np.repeat(np.arange(nl), ns)
    
    sx = sensors[s_idx, 0]
    sy = sensors[s_idx, 1]
    sz = sensors[s_idx, 2]
    
    lx = lights[l_idx, 0]
    ly = lights[l_idx, 1]
    lz = lights[l_idx, 2]
    
    # 3. Calculate distances
    # We want result of shape [num_voxels, ns*nl]
    # Reshape pts to [num_voxels, 1]
    # Reshape lines to [1, ns*nl]
    
    P_x = pts_x[:, np.newaxis]
    P_y = pts_y[:, np.newaxis]
    P_z = pts_z[:, np.newaxis]
    
    S_x = sx[np.newaxis, :]
    S_y = sy[np.newaxis, :]
    S_z = sz[np.newaxis, :]
    
    L_x = lx[np.newaxis, :]
    L_y = ly[np.newaxis, :]
    L_z = lz[np.newaxis, :]
    
    dx = L_x - S_x
    dy = L_y - S_y
    dz = L_z - S_z
    
    seg_len_sq = dx**2 + dy**2 + dz**2
    
    # Avoid div by 0 for zero length segments (though unlikely for sensors/lights)
    seg_len_sq[seg_len_sq == 0] = 1e-10
    
    # Vector from sensor to point
    vx = P_x - S_x
    vy = P_y - S_y
    vz = P_z - S_z
    
    t = (vx * dx + vy * dy + vz * dz) / seg_len_sq
    
    # Clamp t to segment [0, 1]
    # The C++ code checks: if (alpha >= 0.0 && alpha <= 1.0) onSegment=true
    # Else it projects to line?
    # Wait, the C++ code:
    # double xv = x1 - x + alpha * x3; 
    # This is vector from P to Projection Point.
    # x1 + alpha*x3 is the point on the LINE (infinite).
    # So the C++ code calculates distance to the INFINITE line defined by the segment
    # regardless of whether it falls on the segment or not.
    # WAIT! 
    # The struct has `bool onSegment`.
    # But `res.d` is calculated using `xv, yv, zv` which uses `alpha` directly without clamping.
    # So `res.d` is distance to the infinite line.
    # AND `H` uses `res.d` directly!
    # H[i...] = exp(-res.d * res.d * ...);
    # So the `onSegment` flag is computed but NEVER USED in `generateGaussian`.
    # This implies the Gaussian is based on distance to the infinite line passing through sensor and light.
    # This is a bit surprising for a specific "segment", but that matches the C++ code.
    # I will strictly follow the C++ code logic.
    
    closest_x = S_x + t * dx
    closest_y = S_y + t * dy
    closest_z = S_z + t * dz
    
    dist_sq = (P_x - closest_x)**2 + (P_y - closest_y)**2 + (P_z - closest_z)**2
    
    invTwoSigmaSq = 1.0 / (2.0 * sigma * sigma)
    H_mat = np.exp(-dist_sq * invTwoSigmaSq)
    
    # Flatten H:
    # C++ indexing: H[i + dimProd * j]
    # i is voxel index (fastest), j is line index (slowest)
    # Our H_mat is [num_voxels, ns*nl]. Flattening Fortran style will put i first?
    # No, 'F' means first dimension changes fastest.
    # So H_mat.flatten('F') will iterate i (voxel) then j (line).
    # Which matches H[i + dimProd * j].
    
    return H_mat.flatten('F')

def volumeFromHashing(sensors, lights, dim, H, E):
    """
    Python implementation of volumeFromHashing.cpp
    
    Args:
        sensors: [N, 3]
        lights: [M, 3]
        dim: [3]
        H: flattened H
        E: flattened E (or matrix)? In C++ E is passed as double*.
           E corresponds to difference matrix A0 - A.
           In MATLAB, A is m2 x m1. m2 = 4*ns, m1=3*nl?
           Wait, let's check solve_A input Y.
           In C++ volumeFromHashing, L is constructed from E.
           L is size [ns * nl].
           Loop i from 0 to 4*ns*3*nl.
           This implies E has size [4*ns*3*nl] or [4*ns, 3*nl].
           
           sc = i % (4 * ns);
           lc = (i - sc) / (4 * ns);
           This implies i indexes E in column-major order (standard MATLAB/C++-MEX).
           So E is (4*ns) x (3*nl).
           
    Returns:
        V: [nx, ny, nz] volume
    """
    ns = sensors.shape[0]
    nl = lights.shape[0]
    
    # Reconstruct L
    L = np.zeros(ns * nl)
    
    # In Python, we can perform the aggregation more efficiently.
    # E is shape (4*ns, 3*nl).
    # The condition `sc % 4 == lc % 3` selects specific elements.
    # sc goes 0..4*ns-1. s = sc // 4. remainder sc % 4.
    # lc goes 0..3*nl-1. l = lc // 3. remainder lc % 3.
    # We only sum where remainder match.
    # This looks like we are summing blocks.
    # Let's reshape E into (4, ns, 3, nl) -> (4, 3, ns, nl)?
    # No. E is (4*ns, 3*nl).
    # Reshape to (4, ns, 3, nl) only if we account for memory layout.
    # F-order (column major):
    # E[sc, lc]
    # E_reshaped = E.reshape((4, ns, 3, nl), order='F') is WRONG because 
    # dim 0 (rows) is 4*ns. 
    # E.reshape((4, ns, 3*nl), order='F') -> index order is (sc_rem, s, lc)
    
    E_mat = E.reshape((4*ns, 3*nl), order='F')
    
    # We need to sum E[sc, lc] where sc%4 == lc%3.
    # Let's iterate over the remainders k=0,1,2.
    # Since sc%4 can be 3, but lc%3 is only 0,1,2.
    # So we sum for rem=0, rem=1, rem=2.
    
    for r in range(3):
        # Select rows where sc%4 == r
        rows = E_mat[r::4, :] # shape [ns, 3*nl]
        
        # Select cols where lc%3 == r
        cols = rows[:, r::3] # shape [ns, nl]
        
        L += cols.flatten(order='F') # add to L (which is flat ns*nl)
        # Wait, L is indexed L[s + l*ns].
        # In flattened cols (F-order), indices are (s, l).
        # s changes fastest. So index is s + l*ns.
        # This matches.
     
    # Now verify the loop condition: sc%4 == lc%3.
    # Matrix shape (4*ns, 3*nl).
    # For a fixed (s, l), we have a 4x3 block.
    # We are summing the diagonal of the top 3x3 subblock of the 4x3 block?
    # Yes. (0,0), (1,1), (2,2).
    # (3,0), (3,1), (3,2) are never used (sc%4 = 3).
    
    # Now generate Volume.
    # V[i] = sum_j (L[j] * H[i + dimProd*j]) / sum_j (H[i + dimProd*j])
    # array shapes:
    # H_mat = H.reshape((dimProd, ns*nl), order='F')
    # V = (H_mat @ L) / H_mat.sum(axis=1)
    
    dimProd = int(np.prod(dim))
    
    H_mat = H.reshape((dimProd, ns * nl), order='F')
    
    numerator = H_mat @ L
    
    denominator = np.sum(H_mat, axis=1)
    
    # Handle division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        V_flat = numerator / denominator
        V_flat[denominator == 0] = 0
    
    # Reshape V to (nx, ny, nz)
    # C++ returns flat array, but MEX creates 3D array of dim.
    # We should return 3D array.
    V = V_flat.reshape((int(dim[0]), int(dim[1]), int(dim[2])), order='F')
    
    return V

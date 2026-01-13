import jax
import jax.numpy as jnp
from jaxfmm.transf import M2M, M2L, L2L
from jaxfmm.basis import eval_regular_basis, eval_regular_basis_grad, inv_mpl_idx
from jaxfmm.hierarchy import handle_padding
from functools import partial

__all__ = ["eval_potential", "eval_potential_direct"]

@partial(jax.jit, static_argnames=['p', 'mem_limit'])
def get_initial_mpls(padded_pts, padded_chrgs, boxcenters, p, mem_limit = jnp.inf):
    r"""
    Get initial multipole expansions for each box on the highest level.
    """
    mem = padded_chrgs.size * (p+1)**2 * padded_chrgs.dtype.itemsize
    batch_size = int((mem_limit/mem) * boxcenters.shape[0]) + 1 if mem > mem_limit else boxcenters.shape[0]

    def impl_body(args):
        padded_pts_loc, padded_chrgs_loc, boxcenters_loc = args
        dist = padded_pts_loc - boxcenters_loc
        return (eval_regular_basis(dist,p) * padded_chrgs_loc).sum(axis=0)
    return jax.lax.map(impl_body, [padded_pts, padded_chrgs[...,None], boxcenters[:,None,:]], batch_size=batch_size)

@partial(jax.jit, static_argnames=['n_l', 'mem_limit'])
def go_down(coeff, boxcenters, unqs, invs, n_l, mem_limit = jnp.inf):
    r"""
    Using multipole-to-multipole transformation, descend the hierarchy.
    """
    mpls = [coeff]
    for i in range(n_l,0,-1):
        mpls.append(M2M(mpls[-1],boxcenters[i],boxcenters[i-1], unqs, invs, mem_limit))
    return mpls

@partial(jax.jit, static_argnames=['lvl_info', 'mem_limit'])
def go_up(mpls, locs, boxcenters, eval_boxcenters, mpl_cnct, unqs, invs, lvl_info, img_cnct, mem_limit = jnp.inf):
    r"""
    Using multipole-to-local and local-to-local transformation, ascend the hierarchy.
    """
    l_eval, _ = lvl_info[0]
    for j in range(0, l_eval):   # shift the PBC local expansion to the bottom level in the connectivity
        locs = L2L(locs, eval_boxcenters[j], eval_boxcenters[j+1], unqs, invs, mem_limit)

    l_src_max = len(mpls) - 1
    for i in range(len(lvl_info) - 1):  # for every level pair in the connectivity
        l_eval, l_src = lvl_info[i]
        locs += M2L(boxcenters[l_src], eval_boxcenters[l_eval], mpl_cnct[i], unqs, invs, mpls[l_src_max-l_src], img_cnct, mem_limit)
        if(i < (len(lvl_info) - 2)):    # skip direct connectivity at the end
            for j in range(l_eval, lvl_info[i+1][0]):   # move on to the next eval level, shift multiple times if necessary
               locs = L2L(locs,eval_boxcenters[j],eval_boxcenters[j+1], unqs, invs, mem_limit)
    return locs

@partial(jax.jit, static_argnames=['p', 'field', 'mem_limit'])
def eval_local(locs, padded_eval_pts, rev_idcs, boxcenters, p, field = False, mem_limit = jnp.inf):
    r"""
    Evaluate local expansions on the highest level.
    """
    mem = rev_idcs.size * (p+1)**2 * (1+2*field) * locs.dtype.itemsize
    batch_size = int((mem_limit/mem) * locs.shape[0]) + 1 if mem > mem_limit else locs.shape[0]
    def evloc_body(args):
        pts_loc, box_loc, loc_loc = args
        if(field):
            reg = eval_regular_basis_grad(pts_loc - box_loc, p)
            loc_loc = loc_loc[...,None]  # need additional newaxis for vector components
        else:
            reg = eval_regular_basis(pts_loc - box_loc,p)
        ms, _ = inv_mpl_idx(jnp.arange((p+1)**2))
        prefac = ((2-(ms==0))*(1-2*(ms<0)))[None,None,:]
        if(field):
            prefac = prefac[...,None]
        padded_res = (loc_loc * reg * prefac).sum(axis=2)
        return padded_res
    padded_res = jax.lax.map(evloc_body, [padded_eval_pts, boxcenters[:,None], locs[:,None]], batch_size=batch_size)
    if(field):
        return -padded_res.reshape((-1,3))[rev_idcs] / (4*jnp.pi)
    else:
        return padded_res.flatten()[rev_idcs] / (4*jnp.pi)

@partial(jax.jit, static_argnames=['field', 'mem_limit'])
def eval_direct(padded_pts, padded_chrgs, padded_eval_pts, rev_idcs, dir_cnct, img_cnct = jnp.array([[]]), field = False, mem_limit = jnp.inf):
    r"""
    Evaluate the near-field potential directly (P2P).
    """
    if(dir_cnct.shape[1] == 0):   # nothing to compute
        return 0
    nboxs_src = padded_pts.shape[0]
    distsvec = padded_eval_pts[:,None,None,:,:]
    mem = dir_cnct.shape[0] * dir_cnct.shape[1] * padded_eval_pts.shape[1] * padded_pts.dtype.itemsize * 3  # TODO: why do we remove padded_pts.shape[1]? replace with a sqrt of the product with padded_pts.shape[1]?
    batch_size = int((mem_limit/mem) * padded_eval_pts.shape[0]) + 1 if mem > mem_limit else padded_eval_pts.shape[0]

    def dir_batched(args):
        partner, distsvec_loc = args
        if(img_cnct.shape[1] != 0): # PBC enabled
            distsvec_loc -= img_cnct.at[partner//nboxs_src,None,None,:].get(mode="fill",fill_value=jnp.inf) # image offset
            partner %= nboxs_src    # local image position
        distsvec_loc -= padded_pts[partner,:,None,:]
        distsnorm = jnp.linalg.norm(distsvec_loc,axis=-1)
        distsnorm = 1/jnp.where(distsnorm==0,jnp.inf,distsnorm)
        chrgs = padded_chrgs.at[partner].get(mode="fill",fill_value=0.0)
        if(field):
            pot = ((chrgs[...,None]*(distsnorm**3))[...,None] * distsvec_loc).sum(axis=(0,1))
        else:
            pot = (distsnorm*chrgs[...,None]).sum(axis=(0,1))
        return pot
    pot = jax.lax.map(dir_batched, [dir_cnct, distsvec], batch_size = batch_size)
    if(field):
        return pot.reshape((-1,3))[rev_idcs]/(4*jnp.pi)
    else:
        return pot.flatten()[rev_idcs]/(4*jnp.pi)

@partial(jax.jit, static_argnames=['field', 'lvl_info', 'mem_limit'])
def eval_potential(chrgs, pts, eval_pts, idcs, boxcenters, eval_boxcenters, mpl_cnct, dir_cnct, unqs, invs, lvl_info, img_cnct, PBC_op, field = False, mem_limit = jnp.inf, **kwargs):
    r"""
    Evaluate the potential/field via FMM. Requires an array of charge values and the hierarchy information generated by gen_hierarchy.
    """
    if(len(lvl_info) == 1): # only direct interactions - compute potential directly
        return eval_potential_direct(pts,chrgs,eval_pts,field)
    p = invs[-1].shape[0] - 1
    pad_arr = handle_padding(pts, chrgs, eval_pts, idcs)
    coeff = get_initial_mpls(pad_arr[0], pad_arr[1], boxcenters[lvl_info[-2][1]], p, mem_limit)
    mpls = go_down(coeff, boxcenters, unqs, invs, lvl_info[-2][1], mem_limit)
    locs = (PBC_op@mpls[-1][0])[None,:]    # PBC_op is 0 for open boundary conditions
    locs = go_up(mpls, locs, boxcenters, eval_boxcenters, mpl_cnct, unqs, invs, lvl_info, img_cnct, mem_limit)
    return eval_local(locs, pad_arr[2], idcs[1][1], eval_boxcenters[lvl_info[-2][0]], p, field, mem_limit) + \
           eval_direct(pad_arr[3], pad_arr[4], pad_arr[5], idcs[3][1], dir_cnct, img_cnct, field, mem_limit)

@partial(jax.jit, static_argnames=['field'])
def eval_potential_direct(pts, chrgs, eval_pts = None, field = False):
    r"""
    Evaluate the potential directly via pairwise sums.

    :param pts: Array containing point positions.
    :type padded_pts: jnp.array
    :param chrgs: Array containing point charges.
    :type chrgs: jnp.array
    :param eval_pts: Array containing points to evaluate the potential at. Defaults to pts.
    :type eval_pts: jnp.array, optional
    :param field: Optionally evaluate the field (negative gradient) instead of the potential.
    :type field: bool, optional

    :return: Electrostatic potential (or field) of the points and corresponding charges.
    :rtype: jnp.array
    """
    if(eval_pts is None):
        eval_pts = pts
    res = jnp.zeros(eval_pts.shape[:field+1])
    def eval_direct_body(i, val):
        distsvec = pts[:,:] - eval_pts[i,None,:]
        inv_dists = jnp.linalg.norm(distsvec,axis=-1)
        inv_dists = 1/jnp.where(inv_dists==0,jnp.inf,inv_dists) # take out self-interaction
        if(field):
            val = val.at[i].set(-((chrgs * inv_dists**3)[:,None] * distsvec).sum(axis=0))
        else:
            val = val.at[i].set((chrgs * inv_dists).sum())
        return val
    return jax.lax.fori_loop(0,eval_pts.shape[0],eval_direct_body,res)/(4*jnp.pi)
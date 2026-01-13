import numpy as N
import math
import unittest
import traceback # For error logging

eps=1e-3
pi=N.pi

#Interfaces to the user are to be in degrees--internally, we may sometimes convert to radians

def sign(x):
     if x>0: ret=1
     if x<0: ret=-1
     if x==0: ret=0
     return ret

def blkdiag(g):
     glen=len(g); n=0
     for i in range(glen): n=n+g[i].shape[0]
     gout=N.zeros((n,n))
     offset=0
     for i in range(glen):
          currblock=g[i]; lenx,leny=currblock.shape
          for x_ in range(lenx): 
               for y_ in range(leny): 
                    gout[x_+offset,y_+offset]=currblock[x_,y_]
          offset=offset+lenx
     return gout

def similarity_transform(A,B):
     G=N.dot(B,A.transpose()); G2=N.dot(A,G); return G2

def CleanArgs(**args):
     npts=[]
     for name,val in list(args.items()):
          if isinstance(val, (int, float, N.float64, N.int32, N.int16, N.int8)): 
               args[name]=N.array([val], dtype=N.float64); npts.append(1)
          elif isinstance(val, list): 
               if not val: args[name]=N.array([], dtype=N.float64); npts.append(0)
               elif val and isinstance(val[0], (int, float, N.float64, N.int32, N.int16, N.int8)): 
                    args[name]=N.array(val, dtype=N.float64); npts.append(args[name].shape[0])
               elif val and isinstance(val[0], (list, N.ndarray)): 
                    args[name]=N.asarray(val, dtype=N.float64); npts.append(args[name].shape[0])
               else: raise TypeError(f"Unsupported list content for {name}: {val[0]}")
          elif isinstance(val, N.ndarray):
               if val.ndim == 0: args[name]=val.reshape(1); npts.append(1)
               else: npts.append(val.shape[0])
          elif val is None: args[name] = None 
          else: raise TypeError(f"Arg {name} ({type(val)}) is not array-like.")

     maxpts=max(npts) if npts else 1
     for name,val in list(args.items()):
          if val is None: continue 
          if isinstance(val, N.ndarray):
               if val.ndim == 0: val = val.reshape(1); args[name] = val 
               current_len = val.shape[0]
               if current_len < maxpts and val.size > 0 : 
                    last_val_item = val[-1]
                    if val.ndim == 1:
                         addendum = N.full((maxpts - current_len,), last_val_item, dtype=val.dtype)
                         args[name]=N.concatenate((val,addendum))
                    elif val.ndim == 2:
                         addendum_rows = N.tile(last_val_item, ((maxpts - current_len), 1))
                         args[name]=N.concatenate((val,addendum_rows), axis=0)
               elif val.size == 0 and maxpts > 0 : 
                   if val.ndim == 1: args[name] = N.full((maxpts,), N.nan, dtype=N.float64)
     return args

class Instrument(object):
     def __init__(self):
          self.tau_list={'pg(002)':1.87325,'pg(004)':3.74650,'ge(111)':1.92366,'ge(220)':3.14131,'ge(311)':3.68351,'be(002)':3.50702,'2axis':1e-4,'pg(110)':5.49806,'cu(220)':4.91593}
     def get_tau(self,tau): return self.tau_list[tau]
     
class Orientation(object):
     def __init__(self, orient1,orient2):
          self.orient1=N.asarray(orient1, dtype=N.float64)
          self.orient2=N.asarray(orient2, dtype=N.float64)
     
class Lattice(object):
     _a=N.array(0.0);_b=N.array(0.0);_c=N.array(0.0);_alpha=N.array(90.0);_beta=N.array(90.0);_gamma=N.array(90.0)
     _orient1=N.array([[1.,0.,0.]]);_orient2=N.array([[0.,1.,0.]])
     
     def _get_a(self): return self._a
     def _set_a(self,x): self._a=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_b(self): return self._b
     def _set_b(self,x): self._b=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_c(self): return self._c
     def _set_c(self,x): self._c=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_alpha(self): return self._alpha 
     def _set_alpha(self,x): self._alpha=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_beta(self): return self._beta   
     def _set_beta(self,x): self._beta=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_gamma(self): return self._gamma 
     def _set_gamma(self,x): self._gamma=N.asarray(x,dtype=N.float64).reshape(-1); self.setvals()
     def _get_orient1(self): return self._orient1
     def _set_orient1(self,x): self._orient1=N.asarray(x,dtype=N.float64); self.setvals()
     def _get_orient2(self): return self._orient2
     def _set_orient2(self,x): self._orient2=N.asarray(x,dtype=N.float64); self.setvals()

     a=property(_get_a,_set_a); b=property(_get_b,_set_b); c=property(_get_c,_set_c)
     alpha=property(_get_alpha,_set_alpha); beta=property(_get_beta,_set_beta); gamma=property(_get_gamma,_set_gamma)
     orient1=property(_get_orient1,_set_orient1); orient2=property(_get_orient2,_set_orient2)
     
     def __init__(self, a=None, b=None, c=None, alpha=None, beta=None, gamma=None, orient1=None, orient2=None):
          self._a = N.asarray(a if a is not None else 1.0, dtype=N.float64).reshape(-1)
          self._b = N.asarray(b if b is not None else 1.0, dtype=N.float64).reshape(-1)
          self._c = N.asarray(c if c is not None else 1.0, dtype=N.float64).reshape(-1)
          self._alpha = N.asarray(alpha if alpha is not None else 90.0, dtype=N.float64).reshape(-1)
          self._beta = N.asarray(beta if beta is not None else 90.0, dtype=N.float64).reshape(-1)
          self._gamma = N.asarray(gamma if gamma is not None else 90.0, dtype=N.float64).reshape(-1)
          self._orient1 = N.asarray(orient1 if orient1 is not None else [[1,0,0]], dtype=N.float64)
          if self._orient1.ndim == 1: self._orient1 = self._orient1.reshape(1,-1)
          self._orient2 = N.asarray(orient2 if orient2 is not None else [[0,1,0]], dtype=N.float64)
          if self._orient2.ndim == 1: self._orient2 = self._orient2.reshape(1,-1)
          self.setvals()

     def setvals(self):
          params = {'a':self._a,'b':self._b,'c':self._c,'alpha':self._alpha,'beta':self._beta,'gamma':self._gamma,'orient1':self._orient1,'orient2':self._orient2}
          newinput = CleanArgs(**params)
          for name_attr in ['a','b','c','alpha','beta','gamma','orient1','orient2']: setattr(self, f'_{name_attr}', newinput[name_attr])
          self.alphar=N.radians(self._alpha); self.betar=N.radians(self._beta); self.gammar=N.radians(self._gamma) 
          self.star(); self.gtensor('lattice'); self.gtensor('latticestar')
          self.npts = self._a.shape[0] if self._a.ndim > 0 and self._a.size > 0 else 1
          if self.npts == 0 and hasattr(self._a, 'shape') and self._a.shape == (): self.npts = 1
          if self._orient1.shape[0] != self.npts and self.npts > 1 and self._orient1.shape[0] == 1: self._orient1 = N.tile(self._orient1[0], (self.npts, 1))
          if self._orient2.shape[0] != self.npts and self.npts > 1 and self._orient2.shape[0] == 1: self._orient2 = N.tile(self._orient2[0], (self.npts, 1))
          if self._orient1 is not None and self._orient2 is not None:
              self.x,self.y,self.z=StandardSystem(self._orient1,self._orient2,self) 
          else: self.x, self.y, self.z = None, None, None
     
     def star(self): 
          cos_a=N.cos(self.alphar); cos_b=N.cos(self.betar); cos_g=N.cos(self.gammar)
          sin_a=N.sin(self.alphar); sin_b=N.sin(self.betar); sin_g=N.sin(self.gammar)
          sqrt_arg = N.clip(1-cos_a**2-cos_b**2-cos_g**2+2*cos_a*cos_b*cos_g, 0, None)
          self.V = self.a*self.b*self.c*N.sqrt(sqrt_arg)
          self.V = N.where(self.V < eps, eps, self.V) 
          self.astar=(2*N.pi)*self.b*self.c*sin_a/self.V; self.bstar=(2*N.pi)*self.a*self.c*sin_b/self.V; self.cstar=(2*N.pi)*self.a*self.b*sin_g/self.V
          self.alphastar_r=N.arccos(N.clip((cos_b*cos_g-cos_a)/(sin_b*sin_g+eps),-1,1))
          self.betastar_r=N.arccos(N.clip((cos_a*cos_g-cos_b)/(sin_a*sin_g+eps),-1,1))
          self.gammastar_r=N.arccos(N.clip((cos_a*cos_b-cos_g)/(sin_a*sin_b+eps),-1,1))
          self.alphastar=N.degrees(self.alphastar_r); self.betastar=N.degrees(self.betastar_r); self.gammastar=N.degrees(self.gammastar_r)
          self.Vstar=(2*N.pi)**3/self.V
     
     def calc_twotheta(self,wavelength,h,k,l):
          q_mag = self.calc_dhkl_star(h,k,l); q_mag = N.where(q_mag < eps, eps, q_mag)
          d_spacing = (2*N.pi)/q_mag
          arg_asin = N.clip(wavelength/(2*d_spacing), -1.0, 1.0); return N.degrees(2*N.arcsin(arg_asin))
     
     def calc_dhkl_star(self,h,k,l): 
          return N.sqrt(h**2*self.astar**2+k**2*self.bstar**2+l**2*self.cstar**2+2*k*l*self.bstar*self.cstar*N.cos(self.alphastar_r)+2*l*h*self.cstar*self.astar*N.cos(self.betastar_r)+2*h*k*self.astar*self.bstar*N.cos(self.gammastar_r))
 
     def gtensor(self, latticetype):
               num_points = self._a.shape[0] if self._a.ndim > 0 and self._a.size > 0 else 1
               g=N.zeros((3,3,num_points), dtype=N.float64) 
               if latticetype=='lattice': p={'a':self.a,'b':self.b,'c':self.c,'al':self.alphar,'be':self.betar,'ga':self.gammar}
               elif latticetype=='latticestar': p={'a':self.astar,'b':self.bstar,'c':self.cstar,'al':self.alphastar_r,'be':self.betastar_r,'ga':self.gammastar_r}
               else: raise ValueError("latticetype error")
               g[0,0,:]=p['a']**2; g[0,1,:]=p['a']*p['b']*N.cos(p['ga']); g[0,2,:]=p['a']*p['c']*N.cos(p['be'])
               g[1,0,:]=g[0,1,:]; g[1,1,:]=p['b']**2; g[1,2,:]=p['b']*p['c']*N.cos(p['al'])
               g[2,0,:]=g[0,2,:]; g[2,1,:]=g[1,2,:]; g[2,2,:]=p['c']**2
               if latticetype=='lattice': 
                    self.g=g
               else: 
                    self.gstar=g
               return 

def scalar(x1,y1,z1,x2,y2,z2,latticetype,lattice):
     if latticetype=='lattice': p={'a':lattice.a,'b':lattice.b,'c':lattice.c,'al':lattice.alphar,'be':lattice.betar,'ga':lattice.gammar}
     elif latticetype=='latticestar': p={'a':lattice.astar,'b':lattice.bstar,'c':lattice.cstar,'al':lattice.alphastar_r,'be':lattice.betastar_r,'ga':lattice.gammastar_r}
     else: raise ValueError("latticetype error")
     return x1*x2*p['a']**2+y1*y2*p['b']**2+z1*z2*p['c']**2+(x1*y2+x2*y1)*p['a']*p['b']*N.cos(p['ga'])+(x1*z2+x2*z1)*p['a']*p['c']*N.cos(p['be'])+(z1*y2+z2*y1)*p['c']*p['b']*N.cos(p['al'])

def angle2(x,y,z,h,k,l,lattice):
     dot_prod_scaled=(2*N.pi)*(h*x+k*y+l*z)
     mod_r=N.where(modvec(x,y,z,'lattice',lattice)==0,eps,modvec(x,y,z,'lattice',lattice))
     mod_Q=N.where(modvec(h,k,l,'latticestar',lattice)==0,eps,modvec(h,k,l,'latticestar',lattice))
     return N.arccos(N.clip(dot_prod_scaled/(mod_r*mod_Q),-1,1))

def angle(x1,y1,z1,x2,y2,z2,latticetype,lattice):
     mod_v1=N.where(modvec(x1,y1,z1,latticetype,lattice)==0,eps,modvec(x1,y1,z1,latticetype,lattice))
     mod_v2=N.where(modvec(x2,y2,z2,latticetype,lattice)==0,eps,modvec(x2,y2,z2,latticetype,lattice))
     return N.arccos(N.clip(scalar(x1,y1,z1,x2,y2,z2,latticetype,lattice)/(mod_v1*mod_v2),-1,1))

def modvec(x,y,z,latticetype,lattice): return N.sqrt(N.clip(scalar(x,y,z,x,y,z,latticetype,lattice),0,None))
     
def reciprocate(x,y,z,latticetype,lattice):
     g_m = lattice.g if latticetype=='lattice' else lattice.gstar
     return g_m[0,0,:]*x+g_m[0,1,:]*y+g_m[0,2,:]*z, g_m[1,0,:]*x+g_m[1,1,:]*y+g_m[1,2,:]*z, g_m[2,0,:]*x+g_m[2,1,:]*y+g_m[2,2,:]*z

def vector(x1,y1,z1,x2,y2,z2,latticetype,lattice):
     m,vol = (lattice.gstar, lattice.Vstar) if latticetype=='lattice' else (lattice.g, lattice.V)
     s_m=m*vol/((2*N.pi)**2)
     return (y1*z2-z1*y2)*s_m[0,0,:]+(z1*x2-x1*z2)*s_m[1,0,:]+(x1*y2-y1*x2)*s_m[2,0,:], \
            (y1*z2-z1*y2)*s_m[0,1,:]+(z1*x2-x1*z2)*s_m[1,1,:]+(x1*y2-y1*x2)*s_m[2,1,:], \
            (y1*z2-z1*y2)*s_m[0,2,:]+(z1*x2-x1*z2)*s_m[1,2,:]+(x1*y2-y1*x2)*s_m[2,2,:]

def StandardSystem(o1,o2,lattice):
    o1_a = N.asarray(o1, dtype=N.float64); o2_a = N.asarray(o2, dtype=N.float64)
    if o1_a.ndim == 1: o1_a = o1_a.reshape(1, -1)
    if o2_a.ndim == 1: o2_a = o2_a.reshape(1, -1)
    o1_a = o1_a.T; o2_a = o2_a.T 

    try: modx_v=modvec(o1_a[0,:],o1_a[1,:],o1_a[2,:],'latticestar',lattice)
    except IndexError: 
        o1_a=o1_a.T; o2_a=o2_a.T
        modx_v=modvec(o1_a[0,:],o1_a[1,:],o1_a[2,:],'latticestar',lattice)
    
    modx=N.where(modx_v==0,eps,modx_v); x_v=o1_a/modx
    proj=scalar(o2_a[0,:],o2_a[1,:],o2_a[2,:],x_v[0,:],x_v[1,:],x_v[2,:],'latticestar',lattice)
    y_v=o2_a-x_v*proj; mody_v=modvec(y_v[0,:],y_v[1,:],y_v[2,:],'latticestar',lattice)
    
    if N.any(mody_v<=eps): raise ValueError('Orientation vectors are collinear.')
    y_v/=N.where(mody_v==0,eps,mody_v)
    
    z_v=N.array([x_v[1,:]*y_v[2,:]-x_v[2,:]*y_v[1,:],x_v[2,:]*y_v[0,:]-x_v[0,:]*y_v[2,:],x_v[0,:]*y_v[1,:]-x_v[1,:]*y_v[0,:]])
    for v_ortho in [x_v,y_v]: z_v-=scalar(z_v[0,:],z_v[1,:],z_v[2,:],v_ortho[0,:],v_ortho[1,:],v_ortho[2,:],'latticestar',lattice)*v_ortho
    modz_v=modvec(z_v[0,:],z_v[1,:],z_v[2,:],'latticestar',lattice)
    if N.any(modz_v<=eps): raise ValueError('z_vec is zero, problem with orthogonality.')
    z_v/=N.where(modz_v==0,eps,modz_v)
    return x_v,y_v,z_v

def S2R(qx,qy,qz,x,y,z): H=qx*x[0,:]+qy*y[0,:]+qz*z[0,:];K=qx*x[1,:]+qy*y[1,:]+qz*z[1,:];L=qx*x[2,:]+qy*y[2,:]+qz*z[2,:];return H,K,L,N.sqrt(qx**2+qy**2+qz**2)
def R2S(H,K,L,x,y,z,lattice): qx=scalar(H,K,L,x[0,:],x[1,:],x[2,:],'latticestar',lattice);qy=scalar(H,K,L,y[0,:],y[1,:],y[2,:],'latticestar',lattice);qz=scalar(H,K,L,z[0,:],z[1,:],z[2,:],'latticestar',lattice);return qx,qy,qz,modvec(H,K,L,'latticestar',lattice)

def SpecWhere(M2_deg,S1_deg,S2_deg,A2_deg,EXP_list,lattice_obj,orientation_obj,instrument_obj):
     p={'a':lattice_obj._a,'b':lattice_obj._b,'c':lattice_obj._c,'alpha':lattice_obj._alpha,'beta':lattice_obj._beta,'gamma':lattice_obj._gamma,
        'orient1':orientation_obj.orient1,'orient2':orientation_obj.orient2,'M2':M2_deg,'S1':S1_deg,'S2':S2_deg,'A2':A2_deg}
     ni=CleanArgs(**p); cur_o=Orientation(ni['orient1'],ni['orient2'])
     cur_l=Lattice(a=ni['a'],b=ni['b'],c=ni['c'],alpha=ni['alpha'],beta=ni['beta'],gamma=ni['gamma'],orient1=cur_o.orient1,orient2=cur_o.orient2)
     M2r,S1r,S2r,A2r = N.radians(ni['M2']),N.radians(ni['S1']),N.radians(ni['S2']),N.radians(ni['A2'])
     npts=len(EXP_list); taum=N.empty(npts,dtype=N.float64); taua=N.empty(npts,dtype=N.float64)
     for i,e in enumerate(EXP_list): taum[i]=instrument_obj.get_tau(e['mono']['tau']); taua[i]=instrument_obj.get_tau(e['ana']['tau'])
     ki_d=N.sqrt(N.clip(2-2*N.cos(M2r),0,None)); ki_d=N.where(ki_d==0,eps,ki_d); ki=taum/ki_d; Ei=2.072142*ki**2
     kf_d=N.sqrt(N.clip(2-2*N.cos(A2r),0,None)); kf_d=N.where(kf_d==0,eps,kf_d); kf=taua/kf_d; Ef=2.072142*kf**2
     E=Ei-Ef; Q_sq=N.clip(ki**2+kf**2-2*ki*kf*N.cos(S2r),0,None); Q=N.sqrt(Q_sq)
     if cur_l.x is None or cur_l.y is None or cur_l.z is None : return (N.full(npts if npts > 0 else 1,N.nan),)*7 
     ox,oy=cur_l.x,cur_l.y
     safe_den=2*ki*Q; safe_den=N.where(safe_den==0,eps,safe_den); arg_clip = N.clip((Q**2+ki**2-kf**2)/safe_den,-1,1)
     delta=N.absolute(N.arccos(arg_clip)) 
     psi=S1r+delta-N.pi/2; qx=Q*N.cos(psi); qy=Q*N.sin(psi)
     H_val=qx*ox[0,:]+qy*oy[0,:]; K_val=qx*ox[1,:]+qy*oy[1,:]; L_val=qx*ox[2,:]+qy*oy[2,:]
     return H_val, K_val, L_val, E, Q, Ei, Ef 

def SpecGoTo(H,K,L,E,EXP_list,lattice_obj,orientation_obj):
     instrument_obj=Instrument()
     p={'a':lattice_obj._a,'b':lattice_obj._b,'c':lattice_obj._c,'alpha':lattice_obj._alpha,'beta':lattice_obj._beta,'gamma':lattice_obj._gamma,
        'orient1':orientation_obj.orient1,'orient2':orientation_obj.orient2,'H':H,'K':K,'L':L,'E':E}
     ni=CleanArgs(**p); cur_o=Orientation(ni['orient1'],ni['orient2'])
     cur_l=Lattice(a=ni['a'],b=ni['b'],c=ni['c'],alpha=ni['alpha'],beta=ni['beta'],gamma=ni['gamma'],orient1=cur_o.orient1,orient2=cur_o.orient2)
     H_a,K_a,L_a,E_a = ni['H'],ni['K'],ni['L'],ni['E'] 
     C2=2.072142; npts=len(EXP_list)
     taum,taua,infin,efixed = (N.empty((npts,),dtype=N.float64) for _ in range(4))
     for i,e in enumerate(EXP_list):
          taum[i]=instrument_obj.get_tau(e['mono']['tau']); taua[i]=instrument_obj.get_tau(e['ana']['tau'])
          infin[i]=e.get('infin',-1); efixed[i]=e['efixed']
     if cur_l.x is None or cur_l.y is None or cur_l.z is None: return (N.full(npts if npts > 0 else 1,N.nan),)*6
     qx,qy,qz,Q_v=R2S(H_a,K_a,L_a,cur_l.x,cur_l.y,cur_l.z,cur_l)
     ei=efixed+E_a; ef=efixed.copy()
     if E_a.ndim>0 and efixed.ndim>0 and E_a.shape!=efixed.shape: E_ab,ef_b=N.broadcast_arrays(E_a,efixed); ei=ef_b+E_ab; ef=ef_b.copy()
     ch_idx=N.where(infin>0)[0] 
     if ch_idx.size>0:E_as=E_a[ch_idx] if E_a.ndim>0 and E_a.size>1 and ch_idx.max()<E_a.size else E_a; ef[ch_idx]=efixed[ch_idx]-E_as; ei[ch_idx]=efixed[ch_idx]
     ki_sq=ei/C2;ki_sq=N.where(ki_sq<0,N.nan,ki_sq);ki=N.sqrt(ki_sq)
     kf_sq=ef/C2;kf_sq=N.where(kf_sq<0,N.nan,kf_sq);kf=N.sqrt(kf_sq)
     s_ki=N.where(ki==0,eps,ki);s_kf=N.where(kf==0,eps,kf)
     M1=N.arcsin(N.clip(taum/(2*s_ki),-1,1));M2c=2*M1;A1=N.arcsin(N.clip(taua/(2*s_kf),-1,1));A2c=2*A1
     s_2kikf=2*ki*kf;s_2kikf=N.where(s_2kikf==0,eps,s_2kikf);argS2=N.clip((ki**2+kf**2-Q_v**2)/s_2kikf,-1,1);S2c=N.arccos(argS2)
     s_2kiQ=2*ki*Q_v;s_2kiQ=N.where(s_2kiQ==0,eps,s_2kiQ);argDel=N.clip((Q_v**2+ki**2-kf**2)/s_2kiQ,-1,1);delta=N.absolute(N.arccos(argDel))
     psi=N.arctan2(qy,qx);S1c=psi-delta+N.pi/2
     bad_cond=(ei<0)|(ef<0)|(N.abs(taum/(2*s_ki))>1)|(N.abs(taua/(2*s_kf))>1)|(N.isnan(argS2))|(N.isnan(argDel))
     bad=N.where(bad_cond)[0]
     M1[bad]=N.nan;M2c[bad]=N.nan;S1c[bad]=N.nan;S2c[bad]=N.nan;A1[bad]=N.nan;A2c[bad]=N.nan
     return N.degrees(M1),N.degrees(M2c),N.degrees(S1c),N.degrees(S2c),N.degrees(A1),N.degrees(A2c)

# --- Pyodide callable function ---
def parse_vector_str(vec_str, name):
    try:
        s = vec_str.replace('[','').replace(']','').strip()
        if not s: return N.array([0,0,0], dtype=N.float64).reshape(1,3) 
        parts = [float(x.strip()) for x in s.split(',')]
        if len(parts) != 3: raise ValueError(f"{name} must have 3 components")
        return N.array(parts, dtype=N.float64).reshape(1,3)
    except Exception as e:
        raise ValueError(f"Error parsing {name} string '{vec_str}': {e}")

def parse_float_list_str(num_str, name, count=3, default_val=0.0):
    try:
        s = num_str.strip()
        if not s: return N.array([default_val]*count, dtype=N.float64)
        parts = [float(x.strip()) for x in s.split(',')]
        if len(parts) == 1 and count > 1: 
            return N.array([parts[0]]*count, dtype=N.float64)
        if len(parts) != count: raise ValueError(f"{name} must have {count} components or 1 if all same")
        return N.array(parts, dtype=N.float64)
    except Exception as e:
        raise ValueError(f"Error parsing {name} string '{num_str}': {e}")

def py_calculate_hkl_e_from_angles(crystal_system_str, abc_str, angles_str, 
                                   orient1_str, orient2_str, 
                                   fixed_field_str, efixed_val, 
                                   instrument_angles_str):
    try:
        a_vals = parse_float_list_str(abc_str, "a,b,c", 3)
        angle_vals = parse_float_list_str(angles_str, "alpha,beta,gamma", 3, default_val=90.0)

        a,b,c = a_vals[0], a_vals[1], a_vals[2]
        alpha,beta,gamma = angle_vals[0], angle_vals[1], angle_vals[2]

        cs = crystal_system_str.lower()
        if cs == "cubic": a=b=c=a_vals[0]; alpha=beta=gamma=90.0
        elif cs == "tetragonal": a=b=a_vals[0]; c=a_vals[2] if len(a_vals)==3 and a_vals[2]!=0 else a_vals[0]; alpha=beta=gamma=90.0
        elif cs == "orthorhombic": alpha=beta=gamma=90.0 
        elif cs == "hexagonal": a=b=a_vals[0]; c=a_vals[2] if len(a_vals)==3 and a_vals[2]!=0 else a_vals[0]; alpha=beta=90.0; gamma=120.0
        elif cs == "rhombohedral": a=b=c=a_vals[0]; alpha=beta=gamma=angle_vals[0]
        elif cs == "monoclinic": alpha=gamma=90.0 
        
        orient1 = parse_vector_str(orient1_str, "Orientation Vector 1")
        orient2 = parse_vector_str(orient2_str, "Orientation Vector 2")
        
        instr_angles = parse_float_list_str(instrument_angles_str, "Instrument Angles", 4)
        m2_deg, s1_deg, s2_deg, a2_deg = instr_angles[0], instr_angles[1], instr_angles[2], instr_angles[3]

        lattice = Lattice(a,b,c,alpha,beta,gamma,orient1,orient2)
        orientation = Orientation(orient1, orient2) 
        instrument = Instrument()

        exp_item = {
            'mono': {'tau': 'pg(002)'}, 'ana': {'tau': 'pg(002)'}, 
            'efixed': float(efixed_val),
            'infin': -1 if fixed_field_str.upper() == "EI" else 1
        }
        
        H, K, L, E, Q, Ei, Ef = SpecWhere(
            N.array([m2_deg]), N.array([s1_deg]), N.array([s2_deg]), N.array([a2_deg]),
            [exp_item], lattice, orientation, instrument
        )
        
        return {
            "h": H[0], "k": K[0], "l": L[0], "e": E[0], "q": Q[0], 
            "ei": Ei[0], "ef": Ef[0],
            "m2": m2_deg, "s1": s1_deg, "s2": s2_deg, "a2": a2_deg, 
            "m1": "N/A", "a1": "N/A" 
        }
    except Exception as e:
        print(f"Python error: {traceback.format_exc()}") 
        return {"error": str(e)}


# --- Unit Tests ---
class TestLattice(unittest.TestCase): 
    def setUp(self):
        self.a_val=2*N.pi; self.alpha_deg=90.0
        self.orient1_val=N.array([[1,0,0]],dtype=N.float64); self.orient2_val=N.array([[0,1,1]],dtype=N.float64)
        self.fixture=Lattice(a=self.a_val,b=self.a_val,c=self.a_val,alpha=self.alpha_deg,beta=self.alpha_deg,gamma=self.alpha_deg,orient1=self.orient1_val,orient2=self.orient2_val)
    def test_astar(self): self.assertAlmostEqual(self.fixture.astar[0],1.0,3)
    def test_bstar(self): self.assertAlmostEqual(self.fixture.bstar[0],1.0,3)
    def test_cstar(self): self.assertAlmostEqual(self.fixture.cstar[0],1.0,3)
    def test_alphastar(self): self.assertAlmostEqual(self.fixture.alphastar[0],90.0,3)
    def test_V(self): self.assertAlmostEqual(self.fixture.V[0],(2*N.pi)**3,3)
    def test_Vstar(self): self.assertAlmostEqual(self.fixture.Vstar[0],1.0,3) 
    def test_g(self): self.assertAlmostEqual(self.fixture.g[0,0,0],(2*N.pi)**2,3)
    def test_gstar(self): self.assertAlmostEqual(self.fixture.gstar[0,0,0],1.0,3) 
    def test_StandardSystem_x(self): self.assertAlmostEqual(self.fixture.x[0,0],1.0,3)

class TestLatticeCubic(unittest.TestCase):
    def setUp(self): 
        self.a_val=N.array([2*N.pi]); self.alpha_val=N.array([90.0])
        self.orient1_default=N.array([[1,0,0]]); self.orient2_default=N.array([[0,0,1]])
        self.fixture_lattice=Lattice(a=self.a_val,b=self.a_val,c=self.a_val,alpha=self.alpha_val,beta=self.alpha_val,gamma=self.alpha_val,orient1=self.orient1_default,orient2=self.orient2_default)
        self.EXP_config={'ana':{'tau':'pg(002)','mosaic':30},'mono':{'tau':'pg(002)','mosaic':30},'sample':{'mosaic':10,'vmosaic':10},'hcol':N.array([40,10,20,80],dtype=N.float64),'vcol':N.array([120,120,120,120],dtype=N.float64),'efixed':14.7,'method':0,'infin':-1}
        self.instrument=Instrument()
        
    def run_spec_where_test(self,o1,o2,M2,S1,S2,A2,eH,eK,eL,eE,eEi,eEf,infx=1,efix=5.0,lattice_params=None): # Corrected signature
        cur_o=Orientation(o1,o2)
        current_lp_dict = lattice_params if lattice_params else {'a':self.a_val,'b':self.a_val,'c':self.a_val,'alpha':self.alpha_val,'beta':self.alpha_val,'gamma':self.alpha_val}
        
        # Ensure all params passed to Lattice are 1D arrays or scalars as expected by Lattice constructor
        # The Lattice constructor itself now handles .reshape(-1) for a,b,c,alpha,beta,gamma
        final_lp = {}
        for key, val in current_lp_dict.items():
            if isinstance(val, N.ndarray) and val.ndim == 0: # if it's a 0-d array from N.array(scalar)
                final_lp[key] = val.item() # pass scalar
            elif isinstance(val, N.ndarray) and val.ndim == 1 and val.size == 1:
                 final_lp[key] = val[0] # pass scalar from 1-element array
            else:
                 final_lp[key] = val # pass as is (should be scalar or already correct array)
        
        test_l = Lattice(**final_lp, orient1=o1, orient2=o2)
        exp_l=[self.EXP_config.copy()]; exp_l[0]['infix']=infx; exp_l[0]['efixed']=efix
        H,K,L,E,Q,Ei,Ef=SpecWhere(N.array([M2]),N.array([S1]),N.array([S2]),N.array([A2]),exp_l,test_l,cur_o,self.instrument)
        det=f"(Q={Q[0]:.3f} Ei={Ei[0]:.3f} Ef={Ef[0]:.3f})"
        for v,e,n in [(H[0],eH,"H"),(K[0],eK,"K"),(L[0],eL,"L"),(E[0],eE,"E"),(Ei[0],eEi,"Ei"),(Ef[0],eEf,"Ef")]: self.assertAlmostEqual(v,e,3,f'{n} {v:.3f}!={e:.3f} {det}')

    def test_cubic1(self): self.run_spec_where_test(self.orient1_default,self.orient2_default,74.169,97.958,89.131,74.169,1.2999,0.0000,1.7499,0.0000,4.9995,4.9995,efix=5.0)
    def test_cubic2(self): self.run_spec_where_test(self.orient1_default,self.orient2_default,52.420,101.076,70.881,74.169,1.2999,0.0000,1.7499,4.3195,9.3190,4.9995,efix=5.0)     
    def test_cubic3(self): self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),74.169,98.375,109.575,74.169,1.2999,1.2999,1.7499,0.0000,4.9995,4.9995,efix=5.0)        
    def test_cubic4(self): self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),74.169,101.200,109.575,74.169,1.2999,1.2999,1.7499,0.0000,4.9995,4.9995,efix=5.0)    
    def test_cubic5(self): self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),48.661,99.257,80.722,74.169,1.2999,1.2999,1.7499,5.7097,10.7092,4.9995,efix=5.0)   
    def test_cubic6(self): self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),48.661,96.433,80.722,74.169,1.2999,1.2999,1.7499,5.7097,10.7092,4.9995,efix=5.0)  
    def test_tetragonal1(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),74.169,76.720,110.480,74.169,1.2999,0.0000,0.9383,0.0000,4.9995,4.9995,efix=5.0,lattice_params=p)
    def test_tetragonal2(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),49.633,74.345,82.717,74.169,1.2999,0.0000,0.9383,5.3197,10.3192,4.9995,efix=5.0,lattice_params=p)
    def test_tetragonal3(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),89.008,100.569,148.389,89.008,0.9184,0.9184,1.1460,0.0000,3.6997,3.6997,infx=-1,efix=3.7,lattice_params=p)
    def test_tetragonal4(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),89.008,91.561,117.979,98.663,0.7514,0.7514,1.1460,0.5400,3.6997,3.1597,infx=-1,efix=3.7,lattice_params=p)
    def test_tetragonal5(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),89.008,119.133,117.979,98.663,0.7514,0.7514,1.1460,0.5400,3.6997,3.1597,infx=-1,efix=3.7,lattice_params=p)
    def test_tetragonal6(self): p={'a':6.283,'b':6.283,'c':11.765}; self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),89.008,137.820,148.389,89.008,0.9184,0.9184,1.1460,0.0000,3.6997,3.6997,infx=-1,efix=3.7,lattice_params=p)
    def test_orthorhombic1(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),78.930,89.644,86.470,78.930,1.2999,0.0000,0.9383,0.0000,4.4996,4.4996,efix=4.5,lattice_params=p)
    def test_orthorhombic2(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),46.305,98.405,57.515,78.930,1.2999,0.0000,0.9383,7.2594,11.7590,4.4996,efix=4.5,lattice_params=p)
    def test_orthorhombic3(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),78.930,91.228,105.102,78.930,0.8851,0.9664,0.9383,0.0000,4.4996,4.4996,efix=4.5,lattice_params=p) 
    def test_orthorhombic4(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[1,1,0]]),N.array([[0,0,1]]),47.030,92.030,71.391,78.930,0.8851,0.9664,0.9383,6.9194,11.4190,4.4996,efix=4.5,lattice_params=p)
    def test_orthorhombic5(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),47.030,104.676,71.391,78.930,0.8851,0.9664,0.9383,6.9194,11.4190,4.4996,efix=4.5,lattice_params=p)
    def test_orthorhombic6(self): p={'a':6.283,'b':5.7568,'c':11.765}; self.run_spec_where_test(N.array([[0,0,1]]),N.array([[1,1,0]]),78.930,103.874,105.102,78.930,0.8851,0.9664,0.9383,0.0000,4.4996,4.4996,efix=4.5,lattice_params=p)     
    def test_monoclinic1(self): p={'a':N.array([6.283]),'b':N.array([5.7568]),'c':N.array([11.765]),'beta':N.array([100.0])}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),78.930,108.743,130.130,78.930,1.2918,0.0000,0.9262,0.0000,4.4996,4.4996,efix=4.5,lattice_params=p) 
    def test_monoclinic2(self): p={'a':N.array([6.283]),'b':N.array([5.7568]),'c':N.array([11.765]),'beta':N.array([100.0])}; self.run_spec_where_test(N.array([[1,0,0]]),N.array([[0,0,1]]),74.186,106.473,123.991,78.930,1.2918,0.0000,0.9262,0.4979,4.9976,4.4996,efix=4.5,lattice_params=p) 
    def test_monoclinic3(self): p={'a':N.array([6.283]),'b':N.array([5.7568]),'c':N.array([11.765]),'beta':N.array([100.0])}; self.run_spec_where_test(N.array([[1,2,0]]),N.array([[0,0,1]]),78.930,70.753,91.256,78.930,0.6223,1.3563,0.4388,0.0000,4.4996,4.4996,efix=4.5,lattice_params=p) 
    def test_monoclinic4(self): p={'a':N.array([6.283]),'b':N.array([5.7568]),'c':N.array([11.765]),'beta':N.array([100.0])}; self.run_spec_where_test(N.array([[1,2,0]]),N.array([[0,0,1]]),56.239,73.059,73.305,78.930,0.6223,1.3563,0.4388,3.6838,8.1834,4.4996,efix=4.5,lattice_params=p) 

if __name__=="__main__":
     try:
        mylattice = Lattice(a=5.96520,b=5.96520,c=11.702,alpha=90.,beta=90.,gamma=120.) 
        tt = mylattice.calc_twotheta(2.35916,N.array([0.]),N.array([0.]),N.array([2.]))
        print(f"Calculated 2theta for (002): {tt[0]}") 
        
        EXP_main={'ana':{'tau':'pg(002)','mosaic':30},'mono':{'tau':'pg(002)','mosaic':30},'sample':{'mosaic':10,'vmosaic':10},'hcol':N.array([40,10,20,80],dtype=N.float64),'vcol':N.array([120,120,120,120],dtype=N.float64),'infix':-1,'efixed':14.7,'method':0}
        instrument_main=Instrument()  
        if 1: 
              orientation_main=Orientation(N.array([[1,0,0]],dtype=N.float64),N.array([[0,0,1]],dtype=N.float64)) 
              M2_main=N.array([41.177]); A2_main=N.array([41.177]); S1_main=N.array([77.6]); S2_main=N.array([43.5])   
              H_r,K_r,L_r,E_r,Q_r,Ei_r,Ef_r=SpecWhere(M2_main,S1_main,S2_main,A2_main,[EXP_main],mylattice,orientation_main,instrument_main)    
              print(f"Calculated HKL for main: ({H_r[0]:.4f}, {K_r[0]:.4f}, {L_r[0]:.4f})") 
        if 0: 
              orientation_main_goto=Orientation(N.array([[1,0,0]],dtype=N.float64),N.array([[0,1,0]],dtype=N.float64)) 
              H_goto=N.array([1.0]); K_goto=N.array([1.0]); L_goto=N.array([0.0]); W_goto=N.array([0.0]) 
              M1_r,M2_r,S1_r,S2_r,A1_r,A2_r=SpecGoTo(H_goto,K_goto,L_goto,W_goto,[EXP_main],mylattice,orientation_main_goto)
              print((M1_r,M2_r)); print((S1_r,S2_r)); print((A1_r,A2_r))
     except Exception as e:
        print(f"Error in __main__ block: {e}")
    
     print("Running unit tests...")
     unittest.main()

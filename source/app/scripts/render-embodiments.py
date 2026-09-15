from pathlib import Path
import numpy as np
import mujoco,viser,trimesh
import argparse
p=argparse.ArgumentParser()
p.add_argument('--models',type=Path,required=True,help='MuJoCo Menagerie checkout')
p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'public/kinova')
args=p.parse_args()
OUT=args.output
OUT.mkdir(parents=True,exist_ok=True)
server=viser.ViserServer(host='127.0.0.1',port=8098,verbose=False)
server.scene.set_up_direction('+z');server.initial_camera.position=(2.7,2.8,1.9);server.initial_camera.look_at=(0,0,.45)
server.scene.add_grid('/floor',width=3,height=2,cell_size=.1,section_size=.5,plane='xy',plane_opacity=1,plane_color=(250,252,251),cell_color=(225,233,231),section_color=(201,217,212))
robots=[]
for key,title,xml,offset in [('kinova','Kinova Gen3',str(args.models/'kinova_gen3/gen3.xml'),np.array([-.65,0,0])),('franka','Franka Panda',str(args.models/'franka_emika_panda/panda.xml'),np.array([.65,0,0]))]:
 m=mujoco.MjModel.from_xml_path(xml);d=mujoco.MjData(m);home=m.key_qpos[0].copy();d.qpos[:]=home;mujoco.mj_forward(m,d)
 server.scene.add_box('/'+key+'/pedestal',color=(46,64,68),dimensions=(.24,.24,.035),position=offset+np.array([0,0,-.0175]))
 handles=[]
 for gi in range(m.ngeom):
  if m.geom_group[gi]!=2 or m.geom_type[gi]!=mujoco.mjtGeom.mjGEOM_MESH:continue
  mi=m.geom_dataid[gi];va=m.mesh_vertadr[mi];fa=m.mesh_faceadr[mi]
  vertices=m.mesh_vert[va:va+m.mesh_vertnum[mi]];faces=m.mesh_face[fa:fa+m.mesh_facenum[mi]]
  mat=m.geom_matid[gi];rgba=m.mat_rgba[mat] if mat>=0 else m.geom_rgba[gi]
  quat=np.zeros(4);mujoco.mju_mat2Quat(quat,d.geom_xmat[gi])
  h=server.scene.add_mesh_simple(f'/{key}/geom{gi}',vertices=vertices,faces=faces,color=tuple(int(x*255) for x in rgba[:3]),position=d.geom_xpos[gi]+offset,wxyz=quat)
  handles.append((gi,h))
 # Use the Gen3 pinch frame or Panda hand frame as the grasp reference.
 body=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'hand') if key=='franka' else int(m.site_bodyid[0])
 local=np.array([0,0,.105]) if key=='franka' else m.site_pos[0].copy()
 def endpoint():return d.xpos[body]+d.xmat[body].reshape(3,3)@local
 # Gen3's pinch site has its own orientation relative to its wrist.
 site_rot=np.eye(3)
 if key=='kinova':
  flat=np.zeros(9);mujoco.mju_quat2Mat(flat,m.site_quat[0]);site_rot=flat.reshape(3,3)
  local=local+site_rot@np.array([0,0,.094275])
 desired=np.diag([1.,-1.,-1.])
 def solve(target,seed):
  d.qpos[:]=seed
  for _ in range(220):
   mujoco.mj_forward(m,d);pos=endpoint();rotation=d.xmat[body].reshape(3,3)@site_rot
   err=np.r_[target-pos,.5*sum((np.cross(rotation[:,k],desired[:,k]) for k in range(3)))]
   if np.linalg.norm(err)<1e-5:break
   jp=np.zeros((3,m.nv));jr=np.zeros((3,m.nv));mujoco.mj_jac(m,d,jp,jr,pos,body)
   jac=np.vstack([jp[:,:7],jr[:,:7]])
   change=jac.T@np.linalg.solve(jac@jac.T+.002*np.eye(6),err)
   d.qpos[:7]+=np.clip(change,-.09,.09)
   for ji in range(7):
    if m.jnt_limited[ji]:d.qpos[ji]=np.clip(d.qpos[ji],*m.jnt_range[ji])
  return d.qpos.copy()
 target=np.array([.43,-.12,.255]);hover=solve(target+[0,0,.20],home);grasp=solve(target,hover);lift=solve(target+[0,0,.24],grasp)
 # A small desk makes the reach, pickup, and return legible.
 server.scene.add_box('/'+key+'/desk',dimensions=(.34,.36,.025),position=offset+target+[0,0,-.048],color=(204,218,218))
 for lx in [-.13,.13]:
  for ly in [-.14,.14]:server.scene.add_box(f'/{key}/leg{lx}{ly}',dimensions=(.018,.018,.195),position=offset+target+[lx,ly,-.1575],color=(137,160,164))
 mouse_frame=server.scene.add_frame('/'+key+'/mouse',show_axes=False,position=offset+target)
 if key=='franka':
  server.scene.add_box('/'+key+'/mouse/cube',dimensions=(.054,.054,.054),position=(0,0,-.0085),color=(242,132,38))
 else:
  shell=trimesh.creation.icosphere(subdivisions=3,radius=1);shell.vertices*=np.array([.033,.058,.022]);shell.vertices[:,2]=np.maximum(shell.vertices[:,2],-.012)
  server.scene.add_mesh_simple('/'+key+'/mouse/shell',vertices=shell.vertices,faces=shell.faces,color=(38,57,64))
  server.scene.add_box('/'+key+'/mouse/wheel',dimensions=(.008,.017,.007),position=(0,-.025,.022),color=(91,194,185))
  server.scene.add_box('/'+key+'/mouse/seam',dimensions=(.001,.036,.0015),position=(0,-.031,.018),color=(162,178,180))
 fingers=[]
 if key=='kinova':
  grip=server.scene.add_frame('/kinova/gripper',show_axes=False)
  gm=mujoco.MjModel.from_xml_path(str(args.models/'robotiq_2f85/2f85.xml'));gd=mujoco.MjData(gm);mujoco.mj_forward(gm,gd)
  for gi in range(gm.ngeom):
   if gm.geom_group[gi]!=2 or gm.geom_type[gi]!=mujoco.mjtGeom.mjGEOM_MESH:continue
   mi=gm.geom_dataid[gi];va=gm.mesh_vertadr[mi];fa=gm.mesh_faceadr[mi];mat=gm.geom_matid[gi]
   rgba=gm.mat_rgba[mat] if mat>=0 else gm.geom_rgba[gi]
   h=server.scene.add_mesh_simple(f'/kinova/gripper/geom{gi}',vertices=gm.mesh_vert[va:va+gm.mesh_vertnum[mi]],faces=gm.mesh_face[fa:fa+gm.mesh_facenum[mi]],color=tuple(int(x*255) for x in rgba[:3]))
   fingers.append((gi,h))
 else:grip=None
 # Each segment is reach, descend, close, lift, hold, lower, release, retreat.
 poses=[home,hover,grasp,grasp,lift,lift,grasp,grasp,hover,home]
 openings=[.04,.04,.04,.027,.027,.027,.027,.04,.04,.04]
 robots.append((m,d,poses,offset,handles,body,local,site_rot,mouse_frame,target,grip,fingers,openings))
rec=server.get_scene_serializer()
for t in range(451):
 u=min(t/50,8.999999);j=int(u);a=u-j;a=a*a*(3-2*a)
 for m,d,poses,offset,handles,body,local,site_rot,mouse_frame,target,grip,fingers,openings in robots:
  d.qpos[:]=poses[j]*(1-a)+poses[j+1]*a
  opening=openings[j]*(1-a)+openings[j+1]*a
  if m.nq>7:d.qpos[7:]=opening
  mujoco.mj_forward(m,d)
  for gi,h in handles:
   quat=np.zeros(4);mujoco.mju_mat2Quat(quat,d.geom_xmat[gi]);h.position=d.geom_xpos[gi]+offset;h.wxyz=quat
  point=d.xpos[body]+d.xmat[body].reshape(3,3)@local
  mouse_frame.position=offset+(point if 3<=u<6 else target)
  if grip is not None:
   quat=np.zeros(4);mujoco.mju_mat2Quat(quat,(d.xmat[body].reshape(3,3)@site_rot).flatten());grip.position=offset+point-(d.xmat[body].reshape(3,3)@site_rot)@np.array([0,0,.1558]);grip.wxyz=quat
   angle=.05+(.04-opening)/.013*.30
   for ji in range(gm.njnt):
    name=gm.joint(ji).name;gd.qpos[gm.jnt_qposadr[ji]]= -angle if ('coupler' in name or 'follower' in name) else angle
   mujoco.mj_forward(gm,gd)
   for gi,h in fingers:
    quat=np.zeros(4);mujoco.mju_mat2Quat(quat,gd.geom_xmat[gi]);h.position=gd.geom_xpos[gi];h.wxyz=quat
 rec.insert_sleep(1/45)
html=rec.as_html();(OUT/'index.html').write_text(html)
(OUT/'FRANKA-LICENSE.txt').write_text((args.models/'franka_emika_panda/LICENSE').read_text())
(OUT/'MODEL-LICENSE.txt').write_text((args.models/'kinova_gen3/LICENSE').read_text())
(OUT/'ROBOTIQ-LICENSE.txt').write_text((args.models/'robotiq_2f85/LICENSE').read_text())
print('Exported:',len(html),'bytes');server.stop()

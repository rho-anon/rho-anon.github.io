Articulated robot illustration

Kinova Gen3 and Franka Panda models: Google DeepMind MuJoCo Menagerie.
https://github.com/google-deepmind/mujoco_menagerie
Model licenses are provided in this directory.

Viewer: Viser 1.1.0 (Apache-2.0). https://github.com/viser-project/viser
The self-contained viewer runs locally in the browser with no Python server.
The motion is a scripted joint-space illustration, not an experimental rollout,
a measured cross-embodiment transfer result, or a collision-checked trajectory.

Regenerate with Python packages viser==1.1.0, mujoco==3.13.0, numpy, then:
python scripts/render-embodiments.py --models /path/to/mujoco_menagerie

Mouse pickup uses illustrative inverse-kinematics poses and attached objects during grasp. The Gen3 uses the MuJoCo Menagerie Robotiq 2F-85 mesh with illustrative linkage articulation. These are not experimental rollouts or physics-validated grasps. Mouse meshes are procedurally generated. Renderer additionally requires trimesh.

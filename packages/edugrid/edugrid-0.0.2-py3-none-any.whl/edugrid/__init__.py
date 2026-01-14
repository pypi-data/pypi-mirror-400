from gymnasium.envs.registration import register

register(
    id="philsteg/EduGrid-v0",
    entry_point="edugrid.envs.grids:EduGridEnv",
)

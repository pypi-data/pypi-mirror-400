# %% Modules

from dtree import dtree

# %% Create dictionary

dictionary = {}
dictionary["data"] = {}
dictionary["data"]["ab_dataset"] = None
dictionary["data"]["check_dataset"] = None
dictionary["data"]["examples"] = None
dictionary["features"] = {}
dictionary["features"]["config"] = {}
dictionary["features"]["config"]["dense_diffmasif_example"] = None
dictionary["features"]["config"]["dense_diffmasif_features"] = None
dictionary["features"]["config"]["example"] = None
dictionary["features"]["config"]["pair_feature_defaults"] = None
dictionary["features"]["config"]["residue_feature_defaults"] = None
dictionary["features"]["config"]["sparse_diffmasif_example"] = None
dictionary["features"]["config"]["sparse_diffmasif_features"] = None
dictionary["features"]["examples"] = None
dictionary["features"]["test_diffmasif_binding_model"] = None
dictionary["features"]["test_diffmasif_features"] = None
dictionary["features"]["test_diffmasif_transforms"] = None
dictionary["loss"] = {}
dictionary["loss"]["Untitled"] = None
dictionary["masking"] = {}
dictionary["masking"]["test_mask_gens"] = 5
dictionary["model"] = {}
dictionary["model"]["dockgpt"] = {}
dictionary["model"]["dockgpt"]["dockgpt_ga_stats"] = None
dictionary["model"]["dockgpt"]["test_tri_mul"] = None
dictionary["model"]["docking"] = {}
dictionary["model"]["docking"]["docking_stats"] = None
dictionary["model"]["latent_diffusion"] = {}
dictionary["model"]["latent_diffusion"]["Check_OOD_Examples"] = None
dictionary["model"]["latent_diffusion"]["Diffusion_Inference"] = None
dictionary["model"]["latent_diffusion"]["vae_inference"] = None
dictionary["model"]["neodiff"] = {}
dictionary["model"]["neodiff"]["generate_cluster_data"] = None
dictionary["model"]["neodiff"]["neodiff-ipa_tests"] = None
dictionary["model"]["neodiff"]["tests_for_ipa_chain"] = None
dictionary["transforms"] = {}
dictionary["transforms"]["generate_cluster_data_1"] = None
dictionary["transforms"]["generate_cluster_data_2"] = None
dictionary["transforms"]["check_transform_compatibility"] = None

# %% Print tree

dtree(dictionary, "dictionary")

# %% End of script

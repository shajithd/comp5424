# Voxel Displacement Detector
COMP5424 Assignment Voxel Displacement Detector (VDD)

This Slicer module calculates the voxel displacements of two images linear and non-linear methods of
image registration. The resulting displacement field can then be visualised using the Transforms module.


The particular Slicer modules used to compute the linear and non-linear registration is the General Registration (BRAINS) and Demon Registration (BRAINS) respectively.

Procedure:

	1) The VDD takes a baseline MRI scan as the fixed image and a follow-up MRI scan as the moving 
	   image.
	2) Linear Registration is applied using the Affine type with 12 degree-of-freedom.
	3) Non-linear registration is applied with the Diffeomorphic filter type.
	4) Linearly registered image volume is propagated throughout the scene.
	5) Non-linear transform field is visualised in 3D space.

Test:

	Sample baseline and follow up MRI scans are included in the test folder.

This work is part of the University of Sydney, completed in partial fulfilment for credit in Information Technology in Biomedicine. 
Authors: Shajith Dissanayake (USYD)
Technical Supervisors: Sidong Liu (USYD), Tom Cai (USYD)

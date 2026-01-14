import numpy as np
import os
import zarr
import shutil

from .context import line_racer


def test_line_racer_intensity_correction_grid_calculation():

    from line_racer.intensity_correction_precalculation import calculate_correction_grid

    # Define parameters for the correction grid calculation
    gamma_sigma_ratio_minimum = 1e-9
    gamma_sigma_ratio_maximum = 1e6
    sigma_minimum = 1e-5
    sigma_maximum = 1e2
    width_points = 5
    cutoff_minimum = 1
    cutoff_maximum = 5000
    cutoff_points = 5

    # calculate the grid for the Hartmann and cutoff correction
    hartmann = True
    hartmann_cutoff_correction_grid, sigma_grid, gamma_sigma_ratio_grid, cutoff_grid = calculate_correction_grid(
        gamma_sigma_ratio_minimum,
        gamma_sigma_ratio_maximum,
        sigma_minimum, sigma_maximum, width_points,
        cutoff_minimum, cutoff_maximum,
        cutoff_points, hartmann)

    hartmann = False
    cutoff_correction_grid, sigma_grid, gamma_sigma_ratio_grid, cutoff_grid = calculate_correction_grid(
        gamma_sigma_ratio_minimum,
        gamma_sigma_ratio_maximum,
        sigma_minimum, sigma_maximum, width_points,
        cutoff_minimum, cutoff_maximum,
        cutoff_points, hartmann)

    ref_hartmann_cutoff_correction_grid = np.load('tests/reference_files/reference_hartmann_cutoff_correction_grid.npz')
    ref_cutoff_correction_grid = np.load('tests/reference_files/reference_cutoff_correction_grid.npz')

    if not np.allclose(hartmann_cutoff_correction_grid, ref_hartmann_cutoff_correction_grid):
        raise AssertionError("Hartmann cutoff correction grid does not match reference.")
    if not np.allclose(cutoff_correction_grid, ref_cutoff_correction_grid):
        raise AssertionError("Cutoff correction grid does not match reference.")


def test_line_racer_exomol():

    lr = line_racer.line_racer

    # define states file
    upper_state = "           1 14321.54321    211     110      19   e"
    lower_state = "           2 93760.69115    245     122      31   e"

    os.makedirs("exomol_tests/", exist_ok=True)
    with open("exomol_tests/exomol.states", "w") as f:
        f.write(upper_state + "\n")
        f.write(lower_state + "\n")

    # define transition file
    transition = "           1            2 1.2345E-01   187.010999"

    with open("exomol_tests/exomol.trans", "w") as f:
        f.write(transition + "\n")

    # define partition function
    partition1 = "   797.0        295.2217"
    partition2 = "  1800.0        800.0860"

    with open("exomol_tests/exomol.pf", "w") as f:
        f.write(partition1 + "\n")
        f.write(partition2 + "\n")

    temperatures = [797.0, 1800]
    pressures = list(np.logspace(-6, 3, 5))

    # create line racer object
    exomol_test_racer = lr.LineRacer(database="exomol",
                                     input_folder="exomol_tests/",
                                     mass=18.0,
                                     lambda_max=1,  # todo
                                     lambda_min=0.0001,  # todo
                                     hartmann=True,
                                     cutoff=10000,
                                     species_isotope_dict={"1H2-16O": 1.0},
                                     temperatures=temperatures,
                                     pressures=pressures,
                                     broadening_type="constant",
                                     constant_broadening=[0.07, 0.5]
                                     )

    transition_files_list = (
        exomol_test_racer.prepare_opacity_calculation(transition_files_list=['exomol_tests/exomol.trans']))
    final_cross_section_file_name = exomol_test_racer.calculate_opacity(transition_files_list, use_mpi=False)

    store = zarr.storage.ZipStore(final_cross_section_file_name, mode='a')
    z = zarr.group(store=store)
    cross_section_exomol = z['cross-sections']

    store_ref = zarr.storage.ZipStore('tests/reference_files/reference_exomol_cross_section.zarr.zip', mode='a')
    z_ref = zarr.group(store=store_ref)
    ref_cross_section_exomol = z_ref['xsec']

    if not np.allclose(cross_section_exomol[:], ref_cross_section_exomol[:]):
        raise AssertionError("ExoMol cross section does not match reference.")

    shutil.rmtree("cross-sections")
    shutil.rmtree("exomol_tests")


def test_line_racer_hitran():
    lr = line_racer.line_racer

    # define hitran line file
    line = (" 21 1000.004186 1.015E-29 1.989E-06.07660.104 2074.65420.68-.001303       0 1 1 11       0 3 3 01"
            "                    Q 13e     3666632429 9 9 711    27.0   27.0")

    os.makedirs("hitran_tests/", exist_ok=True)
    with open("hitran_tests/hitran.lines", "w") as f:
        f.write(line + "\n")

    temperatures = [296.0, 1000.0]
    pressures = list(np.logspace(-6, 3, 5))

    hitran_test_racer = lr.LineRacer(lambda_min=9.0e-4,
                                     lambda_max=1.1e-3,
                                     database="hitran",
                                     input_folder="hitran_tests/",
                                     species_isotope_dict={"12C-16O": 1.0},
                                     temperatures=temperatures,
                                     pressures=pressures,
                                     broadening_type="hitran_table",
                                     broadening_species_dict={"air": 1.0},
                                     )

    transition_files_list = (
        hitran_test_racer.prepare_opacity_calculation(transition_files_list=['hitran_tests/hitran.lines']))

    final_cross_section_file_name = hitran_test_racer.calculate_opacity(transition_files_list, use_mpi=False)
    store = zarr.storage.ZipStore(final_cross_section_file_name, mode='a')
    z = zarr.group(store=store)
    cross_section_hitran = z['cross-sections']

    store_ref = zarr.storage.ZipStore('tests/reference_files/reference_hitran_cross_section.zarr', mode='a')
    z_ref = zarr.group(store=store_ref)
    ref_cross_section_hitran = z_ref['cross-sections']

    if not np.allclose(cross_section_hitran[:], ref_cross_section_hitran[:]):
        raise AssertionError("HITRAN cross section does not match reference.")


# todo: also do tests for the processing of many lines, could maybe be done using the calculate one pt point function?

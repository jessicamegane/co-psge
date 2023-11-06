declare -a files_to_run=("Horizon120/120_patient10_fold0_allPreproc[4018_82.35]" "Horizon120/120_patient10_fold1_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold2_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold3_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold4_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold5_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold6_allPreproc[4305_88.24]" "Horizon120/120_patient10_fold7_allPreproc[4305_88.24]" "Horizon120/120_patient1_fold0_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold1_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold2_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold3_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold4_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold5_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold6_allPreproc[4018_87.50]" "Horizon120/120_patient1_fold7_allPreproc[4018_87.50]" "Horizon120/120_patient2_fold0_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold1_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold2_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold3_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold4_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold5_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold6_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold7_allPreproc[23247_89.01]" "Horizon120/120_patient2_fold8_allPreproc[23534_90.11]" "Horizon120/120_patient2_fold9_allPreproc[23534_90.11]" "Horizon120/120_patient3_fold0_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold1_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold2_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold3_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold4_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold5_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold6_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold7_allPreproc[23821_90.22]" "Horizon120/120_patient3_fold8_allPreproc[23534_89.13]" "Horizon120/120_patient3_fold9_allPreproc[23534_89.13]" "Horizon120/120_patient4_fold0_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold1_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold2_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold3_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold4_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold5_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold6_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold7_allPreproc[20090_89.74]" "Horizon120/120_patient4_fold8_allPreproc[20377_91.03]" "Horizon120/120_patient4_fold9_allPreproc[20377_91.03]" "Horizon120/120_patient5_fold0_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold1_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold2_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold3_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold4_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold5_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold6_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold7_allPreproc[8036_90.32]" "Horizon120/120_patient5_fold8_allPreproc[7749_87.10]" "Horizon120/120_patient5_fold9_allPreproc[8036_90.32]" "Horizon120/120_patient6_fold0_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold1_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold2_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold3_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold4_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold5_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold6_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold7_allPreproc[12628_89.80]" "Horizon120/120_patient6_fold8_allPreproc[12915_91.84]" "Horizon120/120_patient6_fold9_allPreproc[12628_89.80]" "Horizon120/120_patient7_fold0_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold1_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold2_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold3_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold4_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold5_allPreproc[7175_92.59]" "Horizon120/120_patient7_fold6_allPreproc[7175_92.59]" "Horizon120/120_patient7_fold7_allPreproc[7175_92.59]" "Horizon120/120_patient7_fold8_allPreproc[6888_88.89]" "Horizon120/120_patient7_fold9_allPreproc[6888_88.89]" "Horizon120/120_patient8_fold0_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold1_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold2_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold3_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold4_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold5_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold6_allPreproc[6027_87.50]" "Horizon120/120_patient8_fold7_allPreproc[6027_87.50]" "Horizon120/120_patient9_fold0_allPreproc[6027_91.30]" "Horizon120/120_patient9_fold1_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold2_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold3_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold4_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold5_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold6_allPreproc[5740_86.96]" "Horizon120/120_patient9_fold7_allPreproc[5740_86.96]")

declare -a test_index_start=("4018" "4305" "4305" "4305" "4305" "4305" "4305" "4305" "4018" "4018" "4018" "4018" "4018" "4018" "4018" "4018" "23534" "23534" "23534" "23534" "23534" "23534" "23534" "23247" "23534" "23534" "23821" "23821" "23821" "23821" "23821" "23821" "23821" "23821" "23534" "23534" "20090" "20090" "20090" "20090" "20090" "20090" "20090" "20090" "20377" "20377" "8036" "8036" "8036" "8036" "8036" "8036" "8036" "8036" "7749" "8036" "12628" "12628" "12628" "12628" "12628" "12628" "12628" "12628" "12915" "12628" "6888" "6888" "6888" "6888" "6888" "7175" "7175" "7175" "6888" "6888" "6027" "6027" "6027" "6027" "6027" "6027" "6027" "6027" "6027" "5740" "5740" "5740" "5740" "5740" "5740" "5740")

tLen=${#files_to_run[@]}
for((i=0;i<${tLen};i++));
do
    echo  ${files_to_run[i]} 
    seq 30 | parallel python -m examples.glucose_regression {} ${files_to_run[i]} ${test_index_start[i]}
    #python -m examples.glucose_regression 1 ${files_to_run[i]} 4018
done
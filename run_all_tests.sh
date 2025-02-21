#!/bin/bash
# run $ ./run_all_tests.sh on Git bash
# Exécuter tous les tests un par un
echo "=== Exécution des tests ==="

python -m devicesTests.laser
echo "Test laser finish ✅"

python -m devicesTests.rfgenerator
echo "Test RF Generator finish ✅"

python -m devicesTests.rigol
echo "Test Rigol finish ✅"

python -m devicesTests.rp
echo "Test Red Pitaya finish ✅"

python -m devicesTests.wavemeter
echo "Test Wave Meter finish ✅"

python -m devicesTests.as
echo "Test satured absorption finish ✅"

echo "=== Tous les tests ont été exécutés === ✅"

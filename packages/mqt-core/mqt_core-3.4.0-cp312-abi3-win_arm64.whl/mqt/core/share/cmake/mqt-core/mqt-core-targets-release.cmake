#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "MQT::CoreIR" for configuration "Release"
set_property(TARGET MQT::CoreIR APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreIR PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-ir.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-ir.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreIR )
list(APPEND _cmake_import_check_files_for_MQT::CoreIR "${_IMPORT_PREFIX}/lib/mqt-core-ir.lib" "${_IMPORT_PREFIX}/bin/mqt-core-ir.dll" )

# Import target "MQT::CoreQASM" for configuration "Release"
set_property(TARGET MQT::CoreQASM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQASM PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qasm.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qasm.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQASM )
list(APPEND _cmake_import_check_files_for_MQT::CoreQASM "${_IMPORT_PREFIX}/lib/mqt-core-qasm.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qasm.dll" )

# Import target "MQT::CoreAlgorithms" for configuration "Release"
set_property(TARGET MQT::CoreAlgorithms APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreAlgorithms PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-algorithms.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreCircuitOptimizer"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-algorithms.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreAlgorithms )
list(APPEND _cmake_import_check_files_for_MQT::CoreAlgorithms "${_IMPORT_PREFIX}/lib/mqt-core-algorithms.lib" "${_IMPORT_PREFIX}/bin/mqt-core-algorithms.dll" )

# Import target "MQT::CoreCircuitOptimizer" for configuration "Release"
set_property(TARGET MQT::CoreCircuitOptimizer APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreCircuitOptimizer PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-circuit-optimizer.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-circuit-optimizer.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreCircuitOptimizer )
list(APPEND _cmake_import_check_files_for_MQT::CoreCircuitOptimizer "${_IMPORT_PREFIX}/lib/mqt-core-circuit-optimizer.lib" "${_IMPORT_PREFIX}/bin/mqt-core-circuit-optimizer.dll" )

# Import target "MQT::CoreDS" for configuration "Release"
set_property(TARGET MQT::CoreDS APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreDS PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-ds.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-ds.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreDS )
list(APPEND _cmake_import_check_files_for_MQT::CoreDS "${_IMPORT_PREFIX}/lib/mqt-core-ds.lib" "${_IMPORT_PREFIX}/bin/mqt-core-ds.dll" )

# Import target "MQT::CoreDD" for configuration "Release"
set_property(TARGET MQT::CoreDD APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreDD PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-dd.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-dd.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreDD )
list(APPEND _cmake_import_check_files_for_MQT::CoreDD "${_IMPORT_PREFIX}/lib/mqt-core-dd.lib" "${_IMPORT_PREFIX}/bin/mqt-core-dd.dll" )

# Import target "MQT::CoreZX" for configuration "Release"
set_property(TARGET MQT::CoreZX APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreZX PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-zx.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-zx.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreZX )
list(APPEND _cmake_import_check_files_for_MQT::CoreZX "${_IMPORT_PREFIX}/lib/mqt-core-zx.lib" "${_IMPORT_PREFIX}/bin/mqt-core-zx.dll" )

# Import target "MQT::CoreNAFoMaC" for configuration "Release"
set_property(TARGET MQT::CoreNAFoMaC APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreNAFoMaC PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-na-fomac.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "spdlog::spdlog;MQT::CoreQDMINaDeviceGen"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-na-fomac.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreNAFoMaC )
list(APPEND _cmake_import_check_files_for_MQT::CoreNAFoMaC "${_IMPORT_PREFIX}/lib/mqt-core-na-fomac.lib" "${_IMPORT_PREFIX}/bin/mqt-core-na-fomac.dll" )

# Import target "MQT::CoreNA" for configuration "Release"
set_property(TARGET MQT::CoreNA APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreNA PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-na.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-na.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreNA )
list(APPEND _cmake_import_check_files_for_MQT::CoreNA "${_IMPORT_PREFIX}/lib/mqt-core-na.lib" "${_IMPORT_PREFIX}/bin/mqt-core-na.dll" )

# Import target "MQT::CoreQDMICommon" for configuration "Release"
set_property(TARGET MQT::CoreQDMICommon APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMICommon PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-common.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-common.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMICommon )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMICommon "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-common.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-common.dll" )

# Import target "MQT::CoreQDMI_DDSIM_Device" for configuration "Release"
set_property(TARGET MQT::CoreQDMI_DDSIM_Device APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMI_DDSIM_Device PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-ddsim-device.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreDD;MQT::CoreQASM;MQT::CoreCircuitOptimizer;MQT::CoreQDMICommon;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-ddsim-device.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMI_DDSIM_Device )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMI_DDSIM_Device "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-ddsim-device.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-ddsim-device.dll" )

# Import target "MQT::CoreQDMIScDevice" for configuration "Release"
set_property(TARGET MQT::CoreQDMIScDevice APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMIScDevice PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-sc-device.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreQDMICommon;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-sc-device.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMIScDevice )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMIScDevice "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-sc-device.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-sc-device.dll" )

# Import target "MQT::CoreQDMIScDeviceDyn" for configuration "Release"
set_property(TARGET MQT::CoreQDMIScDeviceDyn APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMIScDeviceDyn PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-sc-device-dyn.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreQDMIScDevice;MQT::CoreQDMICommon;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-sc-device-dyn.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMIScDeviceDyn )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMIScDeviceDyn "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-sc-device-dyn.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-sc-device-dyn.dll" )

# Import target "MQT::CoreQDMINaDeviceGen" for configuration "Release"
set_property(TARGET MQT::CoreQDMINaDeviceGen APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMINaDeviceGen PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device-gen.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device-gen.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMINaDeviceGen )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMINaDeviceGen "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device-gen.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device-gen.dll" )

# Import target "MQT::CoreQDMINaDevice" for configuration "Release"
set_property(TARGET MQT::CoreQDMINaDevice APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMINaDevice PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreQDMICommon;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMINaDevice )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMINaDevice "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device.dll" )

# Import target "MQT::CoreQDMINaDeviceDyn" for configuration "Release"
set_property(TARGET MQT::CoreQDMINaDeviceDyn APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMINaDeviceDyn PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device-dyn.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreQDMINaDevice;MQT::CoreQDMICommon;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device-dyn.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMINaDeviceDyn )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMINaDeviceDyn "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-na-device-dyn.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-na-device-dyn.dll" )

# Import target "MQT::CoreQDMIDriver" for configuration "Release"
set_property(TARGET MQT::CoreQDMIDriver APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreQDMIDriver PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-driver.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "MQT::CoreQDMINaDevice;MQT::CoreQDMIScDevice;MQT::CoreQDMI_DDSIM_Device;spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-driver.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreQDMIDriver )
list(APPEND _cmake_import_check_files_for_MQT::CoreQDMIDriver "${_IMPORT_PREFIX}/lib/mqt-core-qdmi-driver.lib" "${_IMPORT_PREFIX}/bin/mqt-core-qdmi-driver.dll" )

# Import target "MQT::CoreFoMaC" for configuration "Release"
set_property(TARGET MQT::CoreFoMaC APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MQT::CoreFoMaC PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/mqt-core-fomac.lib"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "spdlog::spdlog"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqt-core-fomac.dll"
  )

list(APPEND _cmake_import_check_targets MQT::CoreFoMaC )
list(APPEND _cmake_import_check_files_for_MQT::CoreFoMaC "${_IMPORT_PREFIX}/lib/mqt-core-fomac.lib" "${_IMPORT_PREFIX}/bin/mqt-core-fomac.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

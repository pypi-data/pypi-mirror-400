#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "NCrystal::NCrystal" for configuration "Release"
set_property(TARGET NCrystal::NCrystal APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(NCrystal::NCrystal PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/_ncrystal_core/data/lib/NCrystal.lib"
  IMPORTED_LOCATION_RELEASE "C:/Users/RUNNER~1/AppData/Local/Temp/tmptba_3_xw/wheel/scripts/NCrystal.dll"
  )

list(APPEND _cmake_import_check_targets NCrystal::NCrystal )
list(APPEND _cmake_import_check_files_for_NCrystal::NCrystal "${_IMPORT_PREFIX}/_ncrystal_core/data/lib/NCrystal.lib" "C:/Users/RUNNER~1/AppData/Local/Temp/tmptba_3_xw/wheel/scripts/NCrystal.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

_ncrystal_fixup_ncrystaltargets()

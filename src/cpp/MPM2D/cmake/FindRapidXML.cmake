#
# Search and find the RapidXML library
#

# Search for the include path
find_path(
  RapidXML_INCLUDE_DIR
  NAMES
    rapidxml.hpp
    rapidxml_utils.hpp
    rapidxml_iterators.hpp
    rapidxml_print.hpp
  HINTS "${RapidXML_ROOT_DIR}"
  PATH_SUFFIXES include rapidxml
)

# If we find the library, add it as a target
if (RapidXML_INCLUDE_DIR)
  set(RapidXML_FOUND TRUE)

  # Pull the version number out of the header
  message(DEBUG "Pulling version from ${RapidXML_INCLUDE_DIR}/rapidxml.hpp")
  file(STRINGS "${RapidXML_INCLUDE_DIR}/rapidxml.hpp"
    RapidXML_VERSION REGEX "^//[ ]*Version[ ]+[0-9]+\.[0-9]+[ ]*$")
  string(REGEX REPLACE "^//[ ]*Version[ ]+([0-9]+)\.([0-9]+)[ ]*$" "\\1\.\\2" RapidXML_VERSION "${RapidXML_VERSION}")
  
  # Print a message that we found it
  if (NOT RapidXML_FIND_QUIETLY)
    message(STATUS "Found RapidXML (found version \"${RapidXML_VERSION}\")")
  endif (NOT RapidXML_FIND_QUIETLY)

  # Create a target for it, if there isn't one already created
  if (NOT TARGET RapidXML::RapidXML)
    add_library(RapidXML::RapidXML INTERFACE IMPORTED)
    set_target_properties(RapidXML::RapidXML PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${RapidXML_INCLUDE_DIR}")
  endif (NOT TARGET RapidXML::RapidXML)
else ()
  # If we don't find the library, fail as appropriate
  if (RapidXML_FIND_REQUIRED)  
    message(FATAL_ERROR "RapidXML was NOT found")
  elseif (NOT RapidXML_FIND_QUIETLY)
    message(STATUS "RapidXML was NOT found")
  endif (RapidXML_FIND_REQUIRED)
endif (RapidXML_INCLUDE_DIR)

# Hide the variables that we set
mark_as_advanced(RapidXML_INCLUDE_DIR)

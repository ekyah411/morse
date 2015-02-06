
FILE(GLOB PYTHON_FILES *.py)
INSTALL(FILES ${PYTHON_FILES}
        DESTINATION ${PYTHON_INSTDIR}/morse/builder
        )

INSTALL(DIRECTORY robots
        DESTINATION ${PYTHON_INSTDIR}/morse/builder
        REGEX .*py.$ EXCLUDE
        )

INSTALL(DIRECTORY urdf_components
        DESTINATION ${PYTHON_INSTDIR}/morse/builder
        REGEX .*py.$ EXCLUDE
        )

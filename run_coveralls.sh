#!/bin/bash
if [ "${COVERALLS}" = "true" ]; then
	coveralls -d $1
fi
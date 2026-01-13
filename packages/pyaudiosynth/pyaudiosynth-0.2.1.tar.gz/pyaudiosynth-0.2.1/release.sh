#!/bin/bash


ver="$(hatch project metadata 2>/dev/null | jq '.version' | sed 's/\"//g')"
gh release create $ver --target Main --generate-notes --latest -t v${ver}

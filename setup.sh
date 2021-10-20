#!/bin/bash
me="$(readlink -f "${0}")"
home="$(dirname "${me}")"

cd "${home}"
if [ ! -d ".git" ]; then
	git init .
fi
git submodule add https://github.com/oasis-roles/meta_test tests

rm "${me}"

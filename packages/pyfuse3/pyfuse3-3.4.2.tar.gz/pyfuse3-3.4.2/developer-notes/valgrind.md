To run tests under valgrind:

- Build python `--with-valgrind --with-pydebug`.
- Run `valgrind --trace-children=yes "--trace-children-skip=*mount*" python-dbg -m pytest test/`

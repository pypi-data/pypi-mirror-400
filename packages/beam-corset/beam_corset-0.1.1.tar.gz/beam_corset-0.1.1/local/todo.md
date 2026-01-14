# TODO

## Next Up

- [ ] publish to conda forge?
- [ ] fit with lenses (including lens positions and focal length)
- [x] lens library
  - [ ] with aei lens data
- [ ] more documentation
  - [ ] guides for more advanced features
  - [ ] include part of readme in intro (for nicer repo front page and docs)
- [ ] wherever this is hosted, add a jupyterlite instance with the module installed?
- [ ] lower default resolution in reachability plots to make them faster?
- [ ] no abbreviations in parameter names? consistency?
- [ ] tests
  - [ ] fix old tests
  - [ ] test at least core and solver functionality
  - [ ] add coverage pipeline or something

## Maybe Later

- [ ] extra optimization criteria for underconstrained problems (or posoptimization) **or**
- [ ] reduce similar solutions when there are excess degrees of freedom, maybe add additional optimization criterium?
- [x] analysis
- [ ] multiprocessing (or maybe not, it did not seem to speed it up, maybe the optimizations themselves are already parallel enough)
- [x] sensitivity plots
- [x] docs with sphinx?
  - [x] links in docs
  - [x] provide links to foreign documentation with intersphinx
- [x] refactor solution/candidate/problem?
- [x] more input validation, no region overlaps etc
- [x] data structure with solutions that implements filtering and sorting methods
- [ ] use sympy to build tracers and make optimized function
- [x] error estimates in fitting
- [x] propagate fit error to analysis plots to see if it is withing adjustment range
- [x] fit (with uncertainty?)
- [ ] function to reverse optical setup
- [x] saving and loading of solution? or is this not required since you can just save the notebook?
- [x] use proper gaussian beam transfer matrices
- [x] only store complex beam parameter?
- [ ] optimize coupling for solution list
- [x] propagate fit uncertainty and display in relevant plots
- [ ] fix type annotations to use more general types like ArrayLike
- [x] fix links in notebooks, maybe with a custom converter?
- [x] thick lenses
- [ ] limited quantity of specific lenses
- [x] add coupling axis, the major curvature eigenvector of the reduced sensitivity matrix (of the two least couple DOFs)
- [ ] pipeline including check if notebooks are stripped
- [x] change default filter predicate to ~100% mode matching
- [x] consistency between "population" and "candidate" in docs
- [x] minimum power option for aperture and passage
- [ ] optimize some computations to make them faster?
- [x] make more stuff configurable with config, maybe subobjects?
- [ ] remove contributing and git precommit section from readme
- [ ] use combinations instead of combinations with replacement?

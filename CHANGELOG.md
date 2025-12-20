# Change Log

## [1.0.6] 2022-01-16
### Improvements

- Bump Flask Codebase to [v2stable.0.1](https://github.com/app-generator/boilerplate-code-flask-dashboard/releases)
- Dependencies update (all packages) 
  - Flask==2.0.2 (latest stable version)
  - flask_wtf==1.0.0
  - jinja2==3.0.3
  - flask-restx==0.5.1
- Forms Update:
  - Replace `TextField` (deprecated) with `StringField`

## Unreleased
### Fixes

- 2021-11-08 - `v1.0.6-rc1`
  - ImportError: cannot import name 'TextField' from 'wtforms'
    - Problem caused by `WTForms-3.0.0`
    - Fix: use **WTForms==2.3.3**
    
## [1.0.5] 2021-09-16
### Improvements & Fixes

- Bump Flask Codebase to [v2.0.0](https://github.com/app-generator/boilerplate-code-flask-dashboard/releases)
  - Dependencies update (all packages)
    - Use Flask==2.0.1 (latest stable version)
  - Better Code formatting
  - Improved Files organization
  - Optimize imports
  - Docker Scripts Update 

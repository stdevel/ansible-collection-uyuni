__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  uyuni_host:
    description: Uyuni API endpoint URL
    required: True
  uyuni_port:
    description: Uyuni API endpoint port
    default: 443
  uyuni_verify_ssl:
    description: Verify SSL certificate
    default: True
  uyuni_user:
    description: Uyuni login user
    required: True
  uyuni_password:
    description: Uyuni login password
    required: True
'''

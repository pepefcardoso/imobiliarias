from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Ponto de extensão: is_open_for_signup, save_user etc. quando precisar."""
    pass


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Referenciado em settings mesmo sem provider ativo — fica pronto p/ ativação."""
    pass
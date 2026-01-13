from modeltranslation.translator import register, TranslationOptions
from djangoldp_skill.models import Skill

@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ('name',)

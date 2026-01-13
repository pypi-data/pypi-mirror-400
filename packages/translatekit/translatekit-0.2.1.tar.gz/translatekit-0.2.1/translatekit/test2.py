from base import TranslationConfig
from baidu import BaiduTranslator
import json
# 配置翻译参数
config = TranslationConfig(
    api_key={"appid":"20250405002325015","apikey":"5zNgTyqclEiOghg70Cx3"},  # 百度翻译的appid
    target_lang="zh",  # 目标语言
    debug_mode=True,
    enable_cache=True,
    enable_metrics=True
)

# 创建翻译器实例
translator = BaiduTranslator(config=config)
with open('test_assets\\EN_1D101A.json', 'r',encoding='utf-8') as f:
    json1=json.load(f)
with open('test_assets\\JP_1D101A.json', 'r',encoding='utf-8') as f:
    json2=json.load(f)

diff=translator.get_json_patch(json1,json2)
trans = translator.translate([ok['value'] for ok in diff])
diff_ = [{**i, 'value': s} for i, s in zip(diff, trans)]
ok=translator.apply_json_patch(json1, diff_)
print(ok)
print(translator.get_performance_metrics())
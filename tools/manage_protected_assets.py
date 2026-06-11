from __future__ import annotations
import json, re, sys
from pathlib import Path

ASSET_TYPES = ['exact_secret','pattern_secret','semantic_secret','document_secret']
RISK_LEVELS = ['low','medium','high','critical']

def load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'version':'v24.4-custom-protected-assets','assets':[]}

def save(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def ask(prompt, default=''):
    raw = input(prompt + (f' [{default}]' if default else '') + ': ').strip()
    return raw if raw else default

def ask_choice(prompt, choices, default):
    while True:
        v = ask(f"{prompt} ({', '.join(choices)})", default)
        if v in choices:
            return v
        print('不支援的選項，請只輸入值，不要輸入 name: / value: 這種欄位名稱。')

def ask_bool(prompt, default=True):
    v = ask(prompt + (' (Y/n)' if default else ' (y/N)'), 'Y' if default else 'N').lower()
    return v in {'y','yes','1','true','是'}

def list_assets(data):
    print('\n目前的 protected assets:')
    for i,a in enumerate(data.get('assets',[]),1):
        state='ON' if a.get('enabled',True) else 'OFF'
        src='env_var' if a.get('env_var') else ('pattern' if a.get('pattern') else ('semantic' if a.get('asset_type')=='semantic_secret' else 'value'))
        print(f"{i}. [{state}] {a.get('asset_id','')} | {a.get('name','')} | {a.get('asset_type','')} | risk={a.get('risk_level','')} | source={src}")

def valid_id(asset_id: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9_\-.]+', asset_id or ''))

def add_asset(data):
    print('\n請設定敏感資料 / protected asset。')
    print('asset_type 說明：exact_secret=固定值、pattern_secret=regex、semantic_secret=語意型、document_secret=文件型')
    while True:
        asset_id = ask('asset_id，例如 flag_001 / api_key_pattern')
        if valid_id(asset_id): break
        print('asset_id 只建議使用英文、數字、底線、橫線或點。不要貼 name: / value:。')
    name = ask('name 顯示名稱', asset_id)
    asset_type = ask_choice('asset_type', ASSET_TYPES, 'exact_secret')
    risk = ask_choice('risk_level', RISK_LEVELS, 'high')
    enabled = ask_bool('enabled 是否啟用', True)
    aliases = [x.strip() for x in ask('別名 aliases，使用逗號分隔').split(',') if x.strip()]
    desc = ask('description 描述，可留空')
    item = {'enabled': enabled, 'asset_id': asset_id, 'name': name, 'asset_type': asset_type, 'aliases': aliases, 'risk_level': risk, 'description': desc}
    if asset_type in {'exact_secret','document_secret'}:
        use_env = ask_bool('是否用環境變數保存 secret，避免寫進 JSON', False)
        if use_env:
            item['env_var'] = ask('env_var 名稱，例如 LLM_SECRET_GUARD_TEST_SECRET')
        else:
            item['value'] = ask('secret value，測試用敏感資料', 'picoCTF{flag}')
        item['allow_encoded_detection'] = ask_bool('是否偵測 base64/url/hex 編碼版本', True)
    elif asset_type == 'pattern_secret':
        item['pattern'] = ask('regex pattern')
        item['allow_encoded_detection'] = ask_bool('是否偵測 base64/url/hex 編碼版本', True)
    else:
        item['semantic_labels'] = [x.strip() for x in ask('semantic labels，使用逗號分隔').split(',') if x.strip()]
        item['allow_encoded_detection'] = False
    data.setdefault('assets', []).append(item)
    print('已新增。')

def delete_asset(data):
    list_assets(data)
    v = ask('請輸入要刪除的編號或 asset_id')
    assets = data.get('assets', [])
    idx = None
    if v.isdigit() and 1 <= int(v) <= len(assets):
        idx = int(v)-1
    else:
        for i,a in enumerate(assets):
            if a.get('asset_id') == v:
                idx = i; break
    if idx is None:
        print('找不到。'); return
    removed = assets.pop(idx)
    print(f"已刪除：{removed.get('asset_id')}")

def toggle_asset(data):
    list_assets(data)
    v = ask('請輸入要啟用/停用的編號或 asset_id')
    assets = data.get('assets', [])
    target = None
    if v.isdigit() and 1 <= int(v) <= len(assets):
        target = assets[int(v)-1]
    else:
        target = next((a for a in assets if a.get('asset_id') == v), None)
    if not target:
        print('找不到。'); return
    target['enabled'] = not bool(target.get('enabled', True))
    print(f"{target.get('asset_id')} -> {'ON' if target['enabled'] else 'OFF'}")

def main():
    path = Path(sys.argv[1]) if len(sys.argv)>1 else Path('configs/protected_assets.json')
    data = load(path)
    while True:
        print('\n=== LLM Secret Guard Protected Asset Manager ===')
        print(f'設定檔：{path}')
        print('1. 顯示目前敏感資料')
        print('2. 新增敏感資料')
        print('3. 啟用 / 停用敏感資料')
        print('4. 刪除敏感資料')
        print('5. 儲存並離開')
        print('6. 不儲存離開')
        c = ask('請選擇', '1')
        if c=='1': list_assets(data)
        elif c=='2': add_asset(data)
        elif c=='3': toggle_asset(data)
        elif c=='4': delete_asset(data)
        elif c=='5': save(path,data); print('已儲存。'); return 0
        elif c=='6': print('未儲存。'); return 0
        else: print('不支援的選項。')

if __name__ == '__main__':
    raise SystemExit(main())

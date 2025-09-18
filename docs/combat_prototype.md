# Combat Core Prototype Outline

## Prototype Goals
- 驗證「速度槽決定出手順序」的體感與數值節奏，確保能呈現以快制慢、以慢制快的武俠對決。
- 建立可重複運行的文字戰報輸出流程，為日後掛機模擬與 UI 動畫綁定提供資料接口。
- 測試拆招、反制、狀態與速度調整等核心互動是否能在簡化模型中成立。

## 最小可行範圍
1. **雙方對戰模型**：玩家與 AI 各自持有 1 套招式腳本與基礎屬性（速度、命中、拆招、真氣）。
2. **速度槽演算法**：以 0.25 秒為 tick，累積行動值達門檻（預設 1000）即出手，溢出的餘量保留。
3. **招式解析**：每個招式具備起勢、出招、收勢三段模板，附帶速度調整、命中、傷害與狀態設定。
4. **拆招窗口**：被攻擊者若持有對應拆招招式且行動槽達 60% 以上，可嘗試插入反制。
5. **戰報輸出**：每回合產出 JSON 事件（時間戳、行動者、招式、結果、文字段落、動畫 cue），並聚合成可閱讀的段落。

## 模組分解
- **Simulation Loop**
  ```python
  while not battle_over:
      advance_gauges()
      ready = pick_ready_combatants()
      for actor in ready:
          intent = actor.choose_move()
          counter = check_counter(actor, intent)
          log_setup(actor, intent, counter)
          resolve_mechanics(actor, intent, counter)
          apply_aftermath(actor, intent)
          snapshot_state()
  ```
- **Data Definitions**（YAML）
  ```yaml
  combatant:
    name: "江湖散人"
    baseSpeed: 380
    stats:
      accuracy: 65
      counter: 55
      resilience: 40
    script:
      - if: "enemy.hp_percent < 0.35"
        move: "斷魂刀"
      - if: "self.qi < 40"
        move: "吐納養氣"
      - else: "連環三式"
  ```
- **Narrative Templates**
  - `setup`: "{actor}身形一晃，氣息如潮。"
  - `strike`: "使出《{move}》，刀光連成殘月。"
  - `afterglow`: "{target}被逼得連退數步，真氣震盪。"

## 速度與拆招交互
| 狀況 | 判定條件 | 敘事重點 | 數值結果 |
| ---- | -------- | -------- | -------- |
| 以快打慢 | 攻擊者速度 ≥ 防禦者 + 60 | 「殘影連閃」「前招未息又起後招」 | 攻擊者獲得 `MomentumBonus = +120` 行動值 |
| 以慢制快 | 防禦者速度 ≤ 攻擊者 - 80 且持有柔性拆招 | 「以柔化剛」「後發先至」 | 若拆招成功，攻擊者行動槽清空、受 `slow` |
| 以快制快 | 雙方速度差 < 30 | 「身影交錯」「電光火石」 | 進行搶先檢定：`speed + 隨機(0,30)`，高者先動 |

## 事件樣本
```json
{
  "timestamp": 3.25,
  "actor": "慕容煙",
  "move": "風捲殘雲",
  "phase": "strike",
  "text": "慕容煙腳踏凌波，掌勢如暴雨傾瀉。",
  "animation": "palm_flurry",
  "outcome": {
    "hit": true,
    "damage": 184,
    "status": ["stagger"]
  }
}
```

## 驗證任務
1. **節奏檢查**：以 300 vs 450 速度的角色對戰，確定高速方出手頻率約為 1.5 倍而非無限輪迴。
2. **拆招測試**：設計一組柔性拆招招式，確認對抗爆發型刀法時能觸發反制敘事並重置對手行動槽。
3. **敘事一致性**：模擬 10 回合戰鬥，人工檢視輸出文字是否流暢、動畫 cue 是否合理。
4. **資料輸出**：確保戰報可序列化為 JSON，並提供聚合工具（例如將 5 筆事件組成一段落）。

## 後續擴充點
- 引入多角色混戰與隊伍技能，驗證群戰速度與拆招是否仍穩定。
- 加入怒氣／內勁槽，提供爆發或插招的資源管理層。
- 與掛機系統連動：模擬 10 分鐘掛機戰鬥，統計平均收益與招式熟練度成長。


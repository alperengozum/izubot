## 🔍 POST `/query`

Sisteme bir soru göndererek uygun cevabı almanızı sağlar. Gerekirse `fakulte` filtresiyle sonuçlar daraltılabilir.

### 📥 İstek (Request)

**Content-Type:** `application/json`

#### Gövde (Body) Parametreleri:

| Alan       | Tip    | Zorunlu | Açıklama                                               |
| ---------- | ------ | ------- | ------------------------------------------------------ |
| `question` | string | ✅       | Kullanıcının sorduğu soru.                             |
| `fakulte`  | string | ❌       | (Opsiyonel) Cevapların ait olması istenen fakülte adı. |

#### Örnek İstek:

```json
{
  "question": "Erasmus programına kimler başvurabilir?",
  "fakulte": "İktisadi ve İdari Bilimler Fakültesi"
}
```

---

### 📤 Yanıt (Response)

Başarılı bir sorguda aşağıdaki bilgileri döner:

| Alan      | Tip    | Açıklama                                                              |
| --------- | ------ | --------------------------------------------------------------------- |
| `soru`    | string | Kullanıcının sorduğu orijinal soru.                                   |
| `cevap`   | string | En uygun bulunan yanıtın içeriği.                                     |
| `fakulte` | string | Cevabın ait olduğu fakülte.                                           |
| `konu`    | string | Cevabın ait olduğu konu.                                              |
| `skor`    | float  | Uygunluk puanı (0–1 arasında, ne kadar yüksekse o kadar iyi eşleşme). |

#### Örnek Yanıt:

```json
{
  "soru": "Erasmus programına kimler başvurabilir?",
  "cevap": "Erasmus programına en az 2. sınıf öğrencileri ve 2.20 üzeri not ortalamasına sahip olanlar başvurabilir.",
  "fakulte": "İktisadi ve İdari Bilimler Fakültesi",
  "konu": "Erasmus",
  "skor": 0.894
}
```

---

### ❌ Hatalı Durumlar

* **404 Not Found**

  * Cevap bulunamazsa döner.
  * Yanıt:

    ```json
    {
      "detail": "❌ Uygun bir cevap bulunamadı."
    }
    ```


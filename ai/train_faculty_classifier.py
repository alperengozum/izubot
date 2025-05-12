import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1. Excel dosyasını oku
df = pd.read_excel("IzuBot.xlsx")
df = df.dropna(subset=["Soru", "Fakülte"])

# 2. Veriyi hazırla
X = df["Soru"].values
y = df["Fakülte"].values

# 3. Eğitim ve test setine ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. TF-IDF + Naive Bayes pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB())
])

# 5. Modeli eğit
model.fit(X_train, y_train)

# 6. Başarıyı yazdır
y_pred = model.predict(X_test)
print("🔍 Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred))

# 7. Modeli diske kaydet
with open("faculty_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model eğitildi ve 'faculty_classifier.pkl' olarak kaydedildi.")

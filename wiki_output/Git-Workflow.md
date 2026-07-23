# 🚀 Git Workflow

Selamat datang di panduan resmi alur kerja (workflow) Git untuk project ini. Dokumen ini dirancang sebagai panduan bagi seluruh tim developer agar dapat berkolaborasi dengan rapi, efisien, dan meminimalkan konflik kode.

---

## 📌 1. Pendahuluan

### 🎯 Tujuan Workflow
Tujuan utama dari alur kerja ini adalah untuk menciptakan standar kolaborasi yang bersih, aman, dan dapat dilacak dengan mudah. Dengan adanya workflow yang terstruktur, riwayat (history) pengembangan project akan lebih mudah dipahami oleh seluruh anggota tim.

### 💡 Manfaat Konsistensi
* **Kemudahan Tracking**: Setiap perubahan kode dapat langsung diasosiasikan dengan isu/fitur tertentu di repositori.
* **Minim Konflik**: Mengurangi risiko kode bertabrakan (*merge conflicts*) saat menggabungkan fitur baru.
* **Integrasi Vercel & Deployment yang Aman**: Mencegah deployment otomatis yang tidak terduga pada environment production.
* **Onboarding Cepat**: Memudahkan developer baru untuk memahami bagaimana kontribusi harus dikirimkan.

---

## 🌿 2. Branch Strategy

Project ini membagi area kerja menjadi beberapa branch utama dan pendukung:

### 📢 Branch Utama
1. **`production`**: Branch stabil yang terhubung dengan rilis utama. Hanya menerima merge dari `master` setelah melalui verifikasi manual.
2. **`master`**: Branch utama untuk penggabungan fitur baru yang telah selesai didevelop dan siap dirilis.
3. **`stagging`**: Branch untuk testing lingkungan pra-produksi (staging).

### 🏷️ Naming Convention Branch Pendukung
Setiap kali mulai mengerjakan tugas baru, buat branch baru dari `master` dengan format nama berikut:
* Fitur baru: `feature/nama-fitur` (Contoh: `feature/multi-file-upload`)
* Perbaikan bug/issue: `fix/issue-ISSUE_NUMBER-deskripsi` (Contoh: `fix/issue-57-etl-refresh`)
* Eksperimen/Tugas minor: `chore/deskripsi` (Contoh: `chore/update-readme`)

---

## 🔄 3. Cara Kerja Sehari-hari (Daily Workflow)

Ikuti langkah-langkah di bawah ini setiap hari sebelum dan saat melakukan coding:

### 📥 Langkah 1: Ambil Perubahan Terbaru (Sebelum Mulai)
Sebelum mulai menulis kode baru, pastikan branch lokal Anda sinkron dengan repositori remote agar tidak tertinggal:
```bash
git checkout master
git pull origin master
```

### 🎋 Langkah 2: Buat Branch Kerja Baru
Buat branch baru berdasarkan penamaan konvensional:
```bash
git checkout -b feature/nama-fitur-anda
```

### 💾 Langkah 3: Lakukan Commit Secara Berkala
Jangan menumpuk semua perubahan dalam satu commit raksasa. Buatlah commit kecil yang fokus pada satu perbaikan atau penambahan fungsionalitas.

### 📤 Langkah 4: Sinkronisasi Sebelum Push
Sebelum melakukan push, pastikan Anda menarik update terbaru dari master untuk mendeteksi konflik lebih awal:
```bash
git checkout master
git pull origin master
git checkout feature/nama-fitur-anda
git merge master # Atau: git rebase master
```

---

## 📊 4. Command Cheatsheet

Berikut adalah rangkuman perintah Git yang sering digunakan sehari-hari:

| Perintah | Deskripsi | Kegunaan |
| :--- | :--- | :--- |
| `git checkout -b <branch>` | Membuat branch baru dan langsung berpindah ke sana. | Mulai fitur baru. |
| `git status` | Melihat daftar file yang dimodifikasi, ditambah, atau dihapus. | Memeriksa state saat ini. |
| `git diff` | Menampilkan perubahan detail baris per baris. | Meninjau kode sebelum dicommit. |
| `git add <file>` | Memasukkan file ke dalam staging area. | Menyiapkan file untuk commit. |
| `git commit -m "pesan"` | Menyimpan snapshot perubahan dengan deskripsi. | Mencatat riwayat kode. |
| `git pull origin <branch>` | Mengambil dan menggabungkan perubahan dari remote. | Sinkronisasi lokal. |
| `git push origin <branch>` | Mengirimkan branch dan commit lokal ke remote. | Mempublikasikan kode/PR. |
| `git branch -a` | Menampilkan semua branch (lokal & remote). | Navigasi repositori. |

---

## 🏆 5. Best Practices

### 📝 Commit Message Convention (Wajib #ISSUE_NUMBER)
Untuk mempermudah pelacakan rilis dan otomatisasi integrasi issue, setiap commit message wajib mematuhi aturan berikut:
1. **Wajib mengandung `#ISSUE_NUMBER`** di bagian depan.
2. **Gunakan format konvensional**:
   * `Fix #ISSUE_NUMBER: ...` (Untuk perbaikan bug)
   * `Close #ISSUE_NUMBER: ...` (Untuk menutup task/fitur yang selesai)
   * `Refactor #ISSUE_NUMBER: ...` (Untuk restrukturisasi kode)
   * `#ISSUE_NUMBER: ...` (Untuk perubahan umum)
3. Deskripsi harus singkat, jelas, dan menggunakan Bahasa Indonesia atau Inggris.

### 🛡️ Menghindari Merge Conflict
* **Komunikasi**: Koordinasikan dengan tim jika Anda berencana mengedit file konfigurasi global atau modul inti yang digunakan bersama.
* **Pull Lebih Sering**: Lakukan `git pull` secara teratur agar perbedaan kode antara lokal dan remote tidak terlalu jauh.
* **Rebase**: Gunakan `git rebase` untuk merapikan riwayat commit sebelum mengajukan Pull Request.

### 👯‍♂️ Menangani Kasus "Teman Sudah Push Duluan"
Jika Anda gagal push karena remote sudah diperbarui oleh rekan tim:
1. Simpan pekerjaan Anda ke staging area / commit lokal.
2. Lakukan pull dengan opsi rebase untuk menaruh commit Anda di atas commit terbaru remote:
   ```bash
   git pull origin <nama-branch> --rebase
   ```
3. Jika terjadi konflik, selesaikan konflik pada file yang bertanda, gunakan `git add` pada file tersebut, lalu lanjutkan rebase:
   ```bash
   git rebase --continue
   ```
4. Jika aman, Anda bisa melakukan `git push` seperti biasa.

---

## 💡 6. Contoh Commit Message

### ✅ Contoh yang Baik (Good Examples)
* `Fix #187: perbaiki bug login dengan akun Google`
* `Close #245: tambahkan pagination di daftar produk dashboard`
* `Refactor #310: optimasi query ETL menggunakan Polars`
* `#102: update panduan instalasi di README.md`

### ❌ Contoh yang Buruk (Bad Examples - Jangan Lakukan!)
* `fix bug` *(Terlalu umum & tidak ada nomor issue)*
* `update files` *(Tidak menjelaskan perubahan apa yang dibuat)*
* `menambahkan pagination` *(Kehilangan nomor issue di awal)*
* `Fix: memperbaiki bug login #187` *(Nomor issue ditaruh di belakang, tidak sesuai format)*

---

💡 *Mari kita jaga repositori kita tetap rapi untuk kolaborasi yang lebih menyenangkan! Jika ada pertanyaan mengenai workflow ini, silakan hubungi tim lead.*

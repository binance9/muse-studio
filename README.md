# Muse Studio — Làm phim AI 1-click bằng tiếng Việt

Nạp kịch bản, bấm **1 nút duy nhất** — Muse Studio tự tạo cảnh, tự lồng tiếng Việt, tự sinh nhạc nền, tự cắt ghép thành **một bộ phim hoàn chỉnh** để xem ngay hoặc đăng YouTube/Facebook/TikTok. Chạy ngay trên máy Windows của bạn, **miễn phí 100%**.

---

# ⬇️ TẢI NGAY — bấm là tải, khỏi phải tìm

Chỉ có **3 file**. Tải đủ cả 3 vào thư mục **Downloads** rồi mới sang phần cài đặt ở dưới.

| # | Bấm vào đây để tải | File tải về | Dung lượng |
|---|---|---|---|
| 1 | ⬇️ **[Bộ chạy chính](https://github.com/bitgacon/muse2api/releases/download/v1.6.8/Muse2API_VI_Portable_1.6.8.zip)** | `Muse2API_VI_Portable_1.6.8.zip` | ~67 MB |
| 2 | ⬇️ **[Muse Studio](https://github.com/binance9/muse-studio/archive/refs/heads/main.zip)** | `muse-studio-main.zip` | vài MB |
| 3 | ⬇️ **[Bộ cắt ghép phim](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)** | `ffmpeg-release-essentials.zip` | ~80 MB |

> ⚠️ **Riêng file số 1, nhìn kỹ tên:** chỉ tải file **`Muse2API_VI_Portable_1.6.8.zip`** ở link trên. **Đừng tải file `Muse2API_Update_1.6.7_to_1.6.8.zip`** (~7,5 MB) — đó là bản vá cho người đã có sẵn bản cũ, **chạy một mình sẽ báo lỗi "Failed to load Python DLL ... python312.dll"** và không mở lên được. Link ở bảng trên đã là link đúng, cứ bấm là tải đúng file.

Cài xong, giao diện sẽ trông như thế này:

![Muse Studio — màn hình Thư viện](images/muse-studio-thu-vien.png)

---

## Chuẩn bị — đọc 30 giây

- Máy **Windows 10 hoặc 11 (64-bit)**, có **Google Chrome** (hoặc Microsoft Edge).
- Một **tài khoản muse.ai miễn phí của chính bạn**: vào https://muse.ai, đăng ký bằng email/Google, mất khoảng 1 phút. Tuyệt đối không mua tài khoản của người khác bán.
- Ổ cứng trống khoảng **10 GB**, Internet ổn định.
- **Miễn phí 100%, không có key nào phải mua.** Ai đòi tiền bán key, bán tài khoản, thu tiền "cài hộ" đều là **lừa đảo**. Không bao giờ gửi cho bất kỳ ai: mật khẩu muse.ai, file `.env`, hay cookie đăng nhập của bạn — ai có những thứ đó là chiếm được tài khoản của bạn.

---

## Cài đặt — làm đúng thứ tự 1 → 4, đừng nhảy bước

### Bước 1 — Cài bộ chạy chính

1. Mở thư mục **Downloads**, chuột phải vào file `Muse2API_VI_Portable_1.6.8.zip` → **Extract All…** → **Extract**. Bạn sẽ được một thư mục tên `Muse2API_VI_Portable_1.6.8`.
2. Tạo chỗ chứa cố định: mở ổ **C:** → chuột phải → **New → Folder**, đặt tên là `muse2api-test`. Mở thư mục `muse2api-test` vừa tạo, tạo tiếp một thư mục con tên `app`.
3. **Cắt (Cut)** thư mục `Muse2API_VI_Portable_1.6.8` ở Downloads, **dán (Paste)** vào `C:\muse2api-test\app\`. Kiểm tra lại đường dẫn cho đúng thế này là đạt:
   ```
   C:\muse2api-test\app\Muse2API_VI_Portable_1.6.8\Muse2API_Studio.exe
   ```
4. Mở thư mục đó, nhấp đôi vào **`Muse2API_Studio.exe`**. Nếu Windows hiện màn hình xanh SmartScreen thì bấm **More info → Run anyway**. Chờ chương trình mở lên.
   - Nếu mở EXE mà báo lỗi **"Failed to load Python DLL … python312.dll"**: nghĩa là giải nén chưa hết hoặc đã chép EXE ra chỗ khác làm mất thư mục `_internal` bên cạnh nó. Xóa thư mục đó đi, giải nén lại **toàn bộ** file zip và chạy EXE ngay trong thư mục vừa giải nén.
5. **Thêm tài khoản muse.ai của bạn:** làm theo từng dòng trong file **`HUONG_DAN_1.6.8.txt`** nằm ngay trong thư mục này. Chương trình sẽ mở trình duyệt để bạn tự đăng nhập — chỉ nhập mật khẩu trên trang muse.ai chính thức, không nhập ở bất kỳ chỗ nào khác.
6. **Lấy API key của bạn:** mở file **`.env`** trong cùng thư mục (mở bằng Notepad), tìm dòng bắt đầu bằng `KEY=` — phần chữ phía sau dấu `=` là API key. Ghi lại ở nơi riêng tư, **không gửi cho ai**.
7. **Kiểm tra:** mở Chrome, vào địa chỉ **http://127.0.0.1:18610** — thấy trang quản trị hiện lên là xong Bước 1. **Để nguyên chương trình này chạy**, đừng tắt, trong suốt lúc làm phim.

### Bước 2 — Cài bộ cắt ghép phim

1. Ở thư mục Downloads, chuột phải vào file `ffmpeg-release-essentials.zip` → **Extract All…** → **Extract**. Bạn sẽ được một thư mục tên dài kiểu `ffmpeg-8.x-essentials_build` (số phiên bản có thể khác, kệ nó).
2. **Đổi tên** thư mục đó thành `ffmpeg`.
3. **Cắt (Cut)** thư mục `ffmpeg`, **dán (Paste)** vào `C:\muse2api-test\`.
4. **Kiểm tra:** mở `C:\muse2api-test\ffmpeg\bin` — thấy đủ 2 file `ffmpeg.exe` và `ffprobe.exe` là đạt. Không cần cài thêm gì nữa.

### Bước 3 — Cài Muse Studio + dịch vụ dựng phim

1. Giải nén file `muse-studio-main.zip` ở Downloads (chuột phải → **Extract All…**). Bạn sẽ được thư mục `muse-studio-main`.
2. Mở thư mục `C:\muse2api-test\app\Muse2API_VI_Portable_1.6.8\`, tìm file **`batch.html`** và **đổi tên thành `batch.html.goc.bak`** (giữ bản gốc phòng khi muốn quay lại).
3. Mở thư mục `muse-studio-main\studio\`, chép file **`studio.html`** sang thư mục ở mục 2, rồi **đổi tên `studio.html` thành `batch.html`**.
4. Tạo thư mục `C:\muse2api-test\film-service\`. Mở thư mục `muse-studio-main\film-service\`, chép **cả 2 file** trong đó (`film_service.py` và `analyze_whisper.py`) vào thư mục `film-service` vừa tạo.
5. **Cài Python (chỉ làm 1 lần):** vào https://www.python.org/downloads/ → bấm nút tải **Python 3.12** bản Windows → mở file vừa tải → ở màn hình đầu tiên **tick vào ô "Add python.exe to PATH"** → **Install Now** → cài xong bấm **Close**.
6. **Chạy dịch vụ dựng phim:** bấm phím **Windows** trên bàn phím, gõ `cmd`, bấm **Enter**. Trong cửa sổ đen vừa mở, gõ 2 dòng sau (gõ xong mỗi dòng bấm Enter):
   ```
   cd C:\muse2api-test\film-service
   python film_service.py
   ```
   Cửa sổ hiện thông báo dịch vụ đã chạy ở cổng **18621** là đạt. Mở thêm một tab Chrome vào **http://127.0.0.1:18621/health** — thấy `{"ok": true, ...}` là dịch vụ khỏe. **Giữ cửa sổ cmd này mở** suốt lúc làm phim.
   - Giọng lồng tiếng: dịch vụ tự dùng giọng đọc trực tuyến có sẵn — **không cần cài thêm bất cứ thứ gì**.

### Bước 4 — Mở Muse Studio và làm bộ phim đầu tiên

1. Mở Chrome, vào địa chỉ sau, thay `KEY_CUA_BAN` bằng API key bạn đã lấy ở Bước 1 mục 6:
   ```
   http://127.0.0.1:18610/batch?key=KEY_CUA_BAN
   ```
   Chỉ cần mở bằng địa chỉ có key **đúng 1 lần đầu tiên** — Studio sẽ tự nhớ cho các lần sau.
2. Thấy giao diện Muse Studio với menu bên trái (🎬 Làm phim 1-click · Tạo lẻ · Hàng loạt · Thư viện) là **cài xong**.
3. Vào tab **🎬 Làm phim 1-click**. Tập thử bằng kịch bản mẫu có sẵn trong Studio trước. Kịch bản tự viết thì theo đúng mẫu này — mỗi cảnh gồm 1 dòng `CANH:` và các dòng `THOAI:` ngay dưới nó, giữa các cảnh cách nhau **1 dòng trống**:
   ```
   CANH: <mô tả cảnh bằng tiếng Anh — góc máy, nhân vật, hành động, bối cảnh, ánh sáng>
   THOAI: <Tên nhân vật>: <câu thoại tiếng Việt>

   CANH: <cảnh tiếp theo>
   THOAI: <Tên nhân vật>: <câu thoại>
   ```
   Một tập phim nên có khoảng **10–15 cảnh**, mỗi cảnh quay 10 giây.
4. Muốn nhân vật giống nhau xuyên suốt phim: điền mô tả dàn nhân vật vào ô **Ảnh định trang nhân vật** và bấm nút tạo ảnh định trang trước — hoặc tải ảnh mẫu của bạn lên và đặt vai trò *Nhân vật*. Chọn chế độ khóa:
   - Phim **người thật** → chế độ **Người thật**.
   - Phim **thú / hoạt hình** → chế độ **PRO**.
5. Bấm **▶ LÀM PHIM** và chờ. Trong lúc chạy, **đừng tắt** 3 thứ: chương trình ở Bước 1, cửa sổ cmd ở Bước 3, và tab Studio. Mạng nghẽn là bình thường — tool tự thử lại nhiều lần, cảnh nào xong là lưu ngay; nếu phải dừng giữa chừng, cứ bấm **▶ LÀM PHIM** lại, tool chạy tiếp từ cảnh còn thiếu.
6. **Phim xong** sẽ nằm trong Studio → **Thư viện** → mục **🎬 Phim đã hoàn thành**: xem ngay trong app, ưng rồi mới bấm **⬇ Tải xuống** để lưu về máy. File gốc cũng có sẵn ở `C:\muse2api-test\film-service\outputs\`.

---

## Mỗi lần làm phim tiếp theo — chỉ 3 việc

1. Mở **`Muse2API_Studio.exe`** (thư mục ở Bước 1) và để nó chạy.
2. Mở `cmd`, gõ lại 2 dòng ở Bước 3 mục 6 để chạy dịch vụ dựng phim.
3. Mở Chrome vào **http://127.0.0.1:18610/batch** (không cần nhập key nữa) và làm phim.

---

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Mở EXE báo "Failed to load Python DLL … `python312.dll`" | Tải nhầm file **Update** (~7,5 MB), hoặc giải nén thiếu / chép EXE ra một mình mất thư mục `_internal` | Tải lại đúng file số 1 ở mục **TẢI NGAY** (~67 MB), giải nén **toàn bộ**, chạy EXE ngay trong thư mục vừa giải nén |
| Studio hiện màn hình bắt nhập API key | Chưa từng mở bằng địa chỉ có `?key=` | Mở lại `http://127.0.0.1:18610/batch?key=KEY_CUA_BAN` đúng 1 lần (Bước 4) |
| Vào `127.0.0.1:18610` không thấy gì | Bộ chạy chính chưa mở hoặc đã bị tắt | Mở lại `Muse2API_Studio.exe` (Bước 1), đợi khởi động xong rồi F5 |
| Vào `127.0.0.1:18621/health` không mở được | Dịch vụ dựng phim chưa chạy | Mở `cmd`, chạy lại 2 dòng ở Bước 3 mục 6; đọc dòng lỗi hiện trong cửa sổ cmd nếu có |
| Một cảnh báo lỗi "hết thời hạn chờ" rồi dừng | Phía muse.ai đang nghẽn, xảy ra thường xuyên | Không sao: cảnh đã xong đã được lưu. Bấm **▶ LÀM PHIM** lại, tool chạy tiếp cảnh còn thiếu |
| Tất cả các cảnh đều lỗi liên tục | Đăng nhập tài khoản muse đã hết hạn (thường vài ngày) hoặc hết hạn mức tuần | Thêm lại tài khoản muse của bạn (Bước 1 mục 5); hạn mức tuần tự hồi theo lịch của muse.ai |
| Phim dựng xong nhưng không có tiếng | Bộ cắt ghép phim chưa đúng chỗ, hoặc dịch vụ dựng phim chưa chạy lúc dựng | Kiểm tra đủ `ffmpeg.exe` + `ffprobe.exe` ở `C:\muse2api-test\ffmpeg\bin` (Bước 2) và `/health` (Bước 3), rồi dựng lại |
| Tạo **ảnh** khóa cho nhân vật người thật bị từ chối | Bên tạo ảnh không nhận ảnh người thật làm khung khóa | Dùng chế độ **Người thật** thay cho chế độ PRO khi làm phim người thật |
| Phim xong nhưng không thấy ở đâu | — | Studio → **Thư viện** → **🎬 Phim đã hoàn thành**; hoặc mở thư mục `C:\muse2api-test\film-service\outputs` |

---

## Giữ an toàn cho tài khoản của bạn

- File **`.env`**, thư mục **`data`** và cookie đăng nhập chứa toàn bộ quyền vào tài khoản muse của bạn. **Không gửi, không chia sẻ, không đăng lên mạng** — kể cả "gửi để người ta xem lỗi hộ". Cần chụp màn hình lỗi thì che phần key đi.
- Mọi thứ chỉ chạy trên máy của bạn (`127.0.0.1`), không ai từ Internet vào được — đừng tự mở cổng ra ngoài.
- Nghi ngờ đã lộ key: đổi dòng `KEY=` trong file `.env`, khởi động lại bộ chạy chính, mở lại Studio bằng địa chỉ có key mới.

## Lưu ý nhỏ

- Muốn **đổi chữ ký mặc định trên phim** thành tên của bạn: mở file `batch.html` (chính là Studio đã cài ở Bước 3) tìm chữ `by prompt Thaovy19T` và sửa — chỉ có 1 chỗ.
- Làm phim nhiều cảnh luôn dùng chế độ **độc lập (independent)** — Studio đã mặc định sẵn như vậy, đừng đổi sang chế độ đồng bộ.
- Mỗi cảnh quay tối đa 10 giây — hãy chia kịch bản thành nhiều cảnh ngắn thay vì một cảnh dài.

---

Giấy phép **MIT** (xem file `LICENSE` kèm theo) — dùng, sửa, chia sẻ lại miễn phí.

*Chúc bạn làm được nhiều bộ phim hay — miễn phí, tự tay làm, không mất tiền oan cho ai cả.*

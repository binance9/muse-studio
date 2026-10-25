# Muse Studio — Làm phim AI 1-click bằng tiếng Việt

**Muse Studio** là giao diện tiếng Việt + dịch vụ dựng phim tự động, chạy chung với **Muse2API** trên máy Windows của chính bạn: nạp kịch bản, bấm **1 nút duy nhất**, tool tự tạo ảnh định trang khóa nhân vật, tự quay từng cảnh, tự lồng tiếng Việt, tự sinh nhạc nền, tự cắt ghép + chuyển cảnh theo cấu trúc phim, và xuất ra **một bộ phim hoàn chỉnh** để xem ngay hoặc đăng lên YouTube/Facebook/TikTok.

Repo này chứa đúng 2 phần do cộng đồng đóng góp thêm:

| Phần | File | Việc nó làm |
|---|---|---|
| Giao diện Studio | `studio/studio.html` | Thay cho trang `batch.html` gốc của Muse2API: màn hình làm phim 1-click, tạo lẻ, hàng loạt, thư viện |
| Dịch vụ dựng phim | `film-service/film_service.py` | Lồng tiếng Việt, nhạc nền tự sinh + tự hạ nhỏ dưới thoại, thẻ tên phim, chuyển cảnh, kiểm tra chất lượng, xuất phim |

Phần "động cơ" tạo ảnh/video là **Muse2API** của tác giả gốc (xem mục *Ghi nhận* ở cuối) — repo này **không** chứa động cơ đó, bạn tải riêng ở Bước 1.

---

## ⚠️ CẢNH BÁO LỪA ĐẢO — ĐỌC TRƯỚC KHI TẢI BẤT CỨ THỨ GÌ

- Công cụ này **MIỄN PHÍ 100% và mã nguồn mở**. Bất kỳ ai **bán lại, thu tiền "cài hộ", bán "key kích hoạt", bán tài khoản** đều là **LỪA ĐẢO**. Đừng trả tiền cho bất kỳ ai vì phần mềm này.
- Chỉ tải từ **2 địa chỉ chính thức duy nhất**:
  - Muse Studio (repo này): trang GitHub bạn đang đọc.
  - Muse2API bản gốc: https://github.com/bitgacon/muse2api
- **Không bao giờ** gửi mật khẩu muse.ai, cookie đăng nhập, hay file `.env` cho bất kỳ người nào, kể cả người tự xưng là "hỗ trợ kỹ thuật". Ai có các thứ đó là **chiếm được tài khoản của bạn**.
- **Không có "key" nào phải mua cả.** API key do chính chương trình tự sinh ra trên máy bạn khi cài (nằm trong file `.env`), xem Bước 1. Ai bán key là lừa đảo.
- Cài đặt chỉ khó ở lần đầu. Cứ làm chậm rãi theo từng bước bên dưới, không cần nhờ "dịch vụ cài hộ" nào hết.

---

## Ảnh chụp thực tế

Giao diện Thư viện của Muse Studio đang chạy thật — mỗi video đều hiện sẵn thời lượng (0:10) ở góc dưới để lướt xem nhanh, cột phải là hàng đợi render:

![Muse Studio — màn hình Thư viện](images/muse-studio-thu-vien.png)

---

## Muse Studio làm được gì?

- **Làm phim 1-click:** nạp kịch bản theo mẫu có sẵn, bấm ▶ LÀM PHIM — tool tự làm mọi khâu còn lại.
- **Khóa nhân vật:** tạo 1 ảnh định trang cho cả dàn nhân vật, mọi cảnh đều bám theo ảnh đó để nhân vật không bị "đổi mặt" giữa phim.
- **2 chế độ khóa:** phim **người thật** quay thẳng từng cảnh kèm ảnh mẫu (chế độ *Người thật*); phim **thú / hoạt hình** dùng chế độ *PRO* (tạo ảnh khóa từng cảnh rồi mới quay).
- **Chạy rất "lì" khi mạng nghẽn:** mỗi cảnh tự thử lại **6 lần**, chờ tối đa 12 phút/lần; cảnh nào xong được lưu lại ngay — bấm chạy lại là **chạy tiếp từ cảnh còn thiếu**, không làm lại từ đầu.
- **Lồng tiếng Việt theo vai:** chọn giọng theo nhân vật (nam/nữ, người lớn/trẻ em), hỗ trợ **VieNeu-TTS v3 Turbo** chạy trên máy bạn (không bắt buộc), không có thì tự dùng giọng đọc trực tuyến dự phòng.
- **Nhạc nền tự sinh:** tool tự tạo nhạc nền hợp phim, **tự hạ nhỏ khi có lời thoại** (ducking), âm lượng tổng chuẩn phát sóng −14 LUFS.
- **Dựng chuẩn phim:** thẻ tên phim mở đầu, chuyển cảnh mờ (fade) giữa các cảnh, chữ ký cuối/khung hình theo ý bạn.
- **Phim xong là xem được ngay:** nằm luôn trong mục **🎬 Phim đã hoàn thành** trong Studio — vào app xem trước, **ưng rồi mới bấm ⬇ Tải xuống** để tự lưu về máy. Phim không tự chép đi nơi khác.
- **Mọi video đều hiện thời lượng** ngay trên hình thu nhỏ, không cần bấm vào mới biết dài bao nhiêu.
- Ngoài làm phim: vẫn tạo ảnh/video lẻ, tạo hàng loạt theo danh sách prompt, quản lý thư viện như trang gốc.

---

## Yêu cầu máy tính

- Windows 10 hoặc 11 (64-bit).
- Trình duyệt **Google Chrome** (khuyên dùng) hoặc Microsoft Edge.
- Có tài khoản **muse.ai** (đăng ký miễn phí tại https://muse.ai bằng email/Google của bạn). Đây là tài khoản của chính bạn — **tuyệt đối không dùng tài khoản người khác bán**.
- Ổ cứng trống khoảng **10 GB** (chương trình + model giọng nói + phim xuất ra).
- Kết nối Internet ổn định (tool tạo cảnh qua mạng; mạng yếu thì để tool tự thử lại).
- Không bắt buộc có card đồ họa. Có GPU NVIDIA thì lồng tiếng VieNeu nhanh hơn, không có vẫn chạy được bằng CPU.

> Thứ tự cài đặt: **Bước 1 (Muse2API) → Bước 2 (ffmpeg) → Bước 3 (giao diện Studio) → Bước 4 (dịch vụ dựng phim) → Bước 5 (giọng VieNeu, tuỳ chọn) → Bước 6 (làm bộ phim đầu tiên)**. Đừng bỏ bước.

---

## Bước 1 — Tải và chạy Muse2API (động cơ tạo ảnh/video)

1. **Bấm vào link này để tải thẳng đúng 1 file duy nhất: [Muse2API_VI_Portable_1.6.8.zip](https://github.com/bitgacon/muse2api/releases/download/v1.6.8/Muse2API_VI_Portable_1.6.8.zip)** (bản đầy đủ cho Windows, khoảng 67 MB, từ trang phát hành chính thức của tác giả gốc: https://github.com/bitgacon/muse2api/releases). Chỉ tải ở trang này — file ở nơi khác có thể đã bị gắn mã độc.

   > ⚠️ **ĐỪNG tải nhầm file `Muse2API_Update_1.6.7_to_1.6.8.zip`** (chỉ khoảng 7,5 MB). Đó là bản **vá** dành cho người đã có sẵn bản 1.6.7, **không chạy một mình được**. Nếu tải nhầm rồi mở `Muse2API_Studio.exe` trong thư mục Update, chương trình sẽ báo lỗi **"Failed to load Python DLL ...\_internal\python312.dll — LoadLibrary: The specified module could not be found"** và không mở lên được. Gặp lỗi này thì xóa thư mục Update đó đi, tải lại đúng file Portable ở link trên là xong. Tuyệt đối không lên mạng tải lẻ file `python312.dll` về chép vào.

2. Tạo sẵn cấu trúc thư mục như sau (các bước sau đều dựa trên đúng cấu trúc này, đừng đổi tên):
   ```
   C:\muse2api-test\
   └─ app\
      └─ Muse2API_VI_Portable_1.6.8\   ← giải nén bản portable vào đây
   ```
3. Giải nén **toàn bộ** file zip, giữ nguyên thư mục **`_internal`** nằm bên cạnh EXE (không chép EXE ra một mình, không chạy khi file còn nằm trong zip). Mở thư mục vừa giải nén, chạy **`Muse2API_Studio.exe`** (hoặc file `05_MO_GUI.bat` nếu bản của bạn chạy bằng bat). Đợi chương trình khởi động xong.
4. Trong cửa sổ chương trình, làm theo file `HUONG_DAN_1.6.8.txt` đi kèm để **thêm tài khoản muse.ai của bạn** (đăng nhập bằng tài khoản bạn đã đăng ký ở mục Yêu cầu). Chương trình sẽ mở trình duyệt để bạn tự đăng nhập — mật khẩu chỉ nhập trên trang chính thức của muse.ai, không nhập vào bất kỳ chỗ nào khác.
5. Sau khi thêm tài khoản, chương trình tự sinh **API key** và lưu trong file **`.env`** ngay trong thư mục app. Mở file `.env` bằng Notepad, tìm dòng bắt đầu bằng `KEY=` — phần phía sau dấu `=` là API key của bạn. **Ghi lại key này ở nơi riêng tư và không gửi cho ai.**
6. Kiểm tra động cơ đã chạy: mở trình duyệt vào **http://127.0.0.1:18610** — thấy trang quản trị của Muse2API là đạt. Để nguyên chương trình này chạy trong suốt quá trình làm phim.

> Nếu Windows hiện cảnh báo SmartScreen khi chạy file exe portable: chọn *More info → Run anyway* **chỉ khi** bạn chắc chắn file tải từ đúng trang chính thức ở trên.

## Bước 2 — Cài ffmpeg (dùng để cắt ghép phim)

1. Vào trang chính thức **https://ffmpeg.org/download.html**, chọn bản Windows builds, tải gói **release essentials** dạng `.zip`.
2. Giải nén, bạn sẽ thấy thư mục `bin` chứa `ffmpeg.exe` và `ffprobe.exe`.
3. Chép cả thư mục đó vào đúng vị trí sau:
   ```
   C:\muse2api-test\ffmpeg\bin\ffmpeg.exe
   C:\muse2api-test\ffmpeg\bin\ffprobe.exe
   ```
4. Kiểm tra nhanh: mở thư mục `C:\muse2api-test\ffmpeg\bin`, thấy đủ 2 file trên là đạt (không cần cài thêm gì).

## Bước 3 — Cài giao diện Muse Studio

1. Tải repo này về: bấm nút **Code → Download ZIP** ở đầu trang GitHub rồi giải nén. (Ai rành git thì `git clone` như thường.)
2. Vào thư mục app của Muse2API (`C:\muse2api-test\app\Muse2API_VI_Portable_1.6.8\`), tìm file **`batch.html`** gốc và **đổi tên nó thành `batch.html.goc.bak`** để giữ bản gốc phòng khi muốn quay lại.
3. Chép file **`studio/studio.html`** trong repo này vào đúng thư mục đó và **đổi tên thành `batch.html`**.
4. Mở trình duyệt vào địa chỉ sau, thay `KEY_CUA_BAN` bằng API key bạn đã ghi ở Bước 1:
   ```
   http://127.0.0.1:18610/batch?key=KEY_CUA_BAN
   ```
   Chỉ cần mở bằng địa chỉ có key **đúng 1 lần đầu tiên** — Studio sẽ tự nhớ key cho các lần sau.
5. Thấy giao diện Muse Studio với menu bên trái (🎬 Làm phim 1-click · Tạo lẻ · Hàng loạt · Thư viện) là đạt.

## Bước 4 — Cài dịch vụ dựng phim (film-service)

Dịch vụ này lo phần lồng tiếng, nhạc nền và ghép phim. Không có nó, Studio vẫn tạo được từng cảnh nhưng **không tự dựng thành phim hoàn chỉnh**.

1. Cài **Python 3.12** (64-bit) từ trang chính thức **https://www.python.org/downloads/**. Khi cài, **nhớ tick vào ô "Add python.exe to PATH"** ở màn hình đầu tiên.
2. Tạo thư mục `C:\muse2api-test\film-service\` và chép 2 file trong thư mục `film-service/` của repo này vào đó:
   - `film_service.py` (dịch vụ chính)
   - `synth_vieneu.py` (chỉ dùng nếu bạn cài giọng VieNeu ở Bước 5)
3. Chạy thử: mở **Command Prompt** (gõ `cmd` trong ô tìm kiếm Windows), gõ lần lượt:
   ```
   cd C:\muse2api-test\film-service
   python film_service.py
   ```
   Cửa sổ hiện dòng thông báo dịch vụ đã lắng nghe ở cổng **18621** là đạt. Mở thêm tab trình duyệt vào **http://127.0.0.1:18621/health** — thấy `{"ok": true, ...}` là dịch vụ khỏe.
4. **Đặt tự khởi động cùng Windows** (làm 1 lần, để khỏi phải mở tay mỗi lần):
   - Mở **Task Scheduler** (gõ `Task Scheduler` trong ô tìm kiếm Windows) → *Create Task…*
   - Tab **General**: đặt tên `MuseFilmService`.
   - Tab **Triggers** → *New…* → chọn **At log on** → OK.
   - Tab **Actions** → *New…* → **Program/script**: đường dẫn tới `python.exe` (thường là `C:\Users\<tên-bạn>\AppData\Local\Programs\Python\Python312\python.exe` — kiểm tra bằng lệnh `where python` trong cmd); **Add arguments**: `film_service.py`; **Start in**: `C:\muse2api-test\film-service` → OK.
   - Bấm OK lưu lại, chuột phải vào task vừa tạo → **Run** để chạy ngay lần này.
   - Kiểm tra lại bằng địa chỉ `/health` ở trên.
5. Để nguyên dịch vụ chạy nền như vậy trong lúc làm phim.

## Bước 5 — (Tuỳ chọn) Cài giọng lồng tiếng VieNeu-TTS

Không cài bước này vẫn làm phim được — dịch vụ tự dùng giọng đọc trực tuyến dự phòng. Cài VieNeu thì giọng tiếng Việt tự nhiên hơn và chạy hoàn toàn trên máy bạn.

1. Mở Command Prompt, tạo môi trường riêng:
   ```
   cd C:\muse2api-test
   py -3.12 -m venv tts-pro\venv
   tts-pro\venv\Scripts\python -m pip install --upgrade pip
   tts-pro\venv\Scripts\python -m pip install vieneu==3.8.3
   ```
2. Chép file `synth_vieneu.py` (đã chép ở Bước 4) vào thư mục `C:\muse2api-test\tts-pro\` — cạnh thư mục `venv` vừa tạo.
3. Lần lồng tiếng đầu tiên, VieNeu sẽ **tự tải model khoảng 2 GB** từ kho model công khai của dự án VieNeu-TTS — cứ để nó tải xong, các lần sau không tải lại. Model tải xong nằm trong `tts-pro\model`.
4. Từ đây dịch vụ dựng phim tự nhận diện VieNeu và dùng nó để lồng tiếng, không cần cấu hình thêm.

> VieNeu-TTS là dự án độc lập của tác giả khác (tìm đúng tên "VieNeu-TTS" trên GitHub/Hugging Face). Chỉ tải model từ trang chính thức của dự án đó.

## Bước 6 — Làm bộ phim đầu tiên

1. Mở Muse Studio (địa chỉ ở Bước 3), vào tab **🎬 Làm phim 1-click**.
2. Tập thử bằng kịch bản mẫu có sẵn trong Studio trước để chắc chắn mọi thứ chạy. Kịch bản tự viết theo đúng định dạng này — mỗi cảnh gồm 1 dòng `CANH:` và các dòng `THOAI:` ngay dưới nó:
   ```
   CANH: <mô tả cảnh bằng tiếng Anh — góc máy, nhân vật, hành động, bối cảnh, ánh sáng>
   THOAI: <Tên nhân vật>: <câu thoại tiếng Việt>

   CANH: <cảnh tiếp theo>
   THOAI: <Tên nhân vật>: <câu thoại>
   ```
   Giữa các cảnh cách nhau **1 dòng trống**. Một tập phim nên có khoảng 10–15 cảnh, mỗi cảnh tool quay 10 giây.
3. Muốn nhân vật giống nhau xuyên suốt phim: điền mô tả dàn nhân vật vào ô **Ảnh định trang nhân vật** và bấm nút tạo ảnh định trang trước — hoặc tải ảnh mẫu của bạn lên và đặt vai trò *Nhân vật*.
4. Chọn chế độ khóa nhân vật:
   - Phim **người thật** → chọn chế độ **Người thật** (quay thẳng từng cảnh + ảnh mẫu).
   - Phim **thú / hoạt hình** → chọn chế độ **PRO**.
5. Bấm **▶ LÀM PHIM** và chờ. Đừng tắt Muse2API, dịch vụ dựng phim và tab Studio trong lúc chạy. Mạng nghẽn là chuyện bình thường: tool tự thử lại, cảnh nào xong là lưu — nếu phải dừng giữa chừng, cứ **bấm ▶ LÀM PHIM lại**, tool chạy tiếp từ cảnh còn thiếu.
6. Phim xong sẽ:
   - Phát ngay trong Studio và nằm ở mục **🎬 Phim đã hoàn thành** trong **Thư viện** (kéo xuống dưới danh sách clip lẻ) — lúc nào mở Studio cũng xem lại / tải lại được.
   - File gốc nằm ở `C:\muse2api-test\film-service\outputs\`.

---

## Các lỗi thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Mở `Muse2API_Studio.exe` báo "Failed to load Python DLL ... `python312.dll`" | Đã tải nhầm file **Update** (~7,5 MB) thay vì bản **Portable** đầy đủ (~67 MB), hoặc giải nén thiếu / chép EXE ra một mình làm mất thư mục `_internal` | Xóa bản đó đi, tải lại đúng file Portable bằng link tải thẳng ở Bước 1, giải nén **toàn bộ** và chạy EXE ngay trong thư mục vừa giải nén, giữ nguyên `_internal` bên cạnh EXE |
| Studio hiện màn hình bắt nhập API key | Chưa từng mở bằng địa chỉ có `?key=` | Mở lại `http://127.0.0.1:18610/batch?key=KEY_CUA_BAN` đúng 1 lần (Bước 3) |
| Vào `127.0.0.1:18610` không thấy gì | Muse2API chưa chạy hoặc đã tắt | Mở lại `Muse2API_Studio.exe` ở Bước 1, đợi khởi động xong rồi F5 |
| `/health` của film-service không mở được | Dịch vụ dựng phim chưa chạy | Chạy tay `python film_service.py` trong `C:\muse2api-test\film-service` để xem lỗi hiện ra, hoặc kiểm tra task `MuseFilmService` ở Bước 4 |
| Một cảnh báo lỗi "hết thời hạn chờ" rồi dừng | Phía muse.ai đang nghẽn, chuyện xảy ra thường xuyên | Không sao cả: các cảnh đã xong đã được lưu. Bấm **▶ LÀM PHIM** lại, tool chạy tiếp cảnh còn thiếu. Bản Studio này đã tự thử lại 6 lần/cảnh trước khi dừng |
| Tất cả các cảnh đều lỗi liên tục | Phiên đăng nhập tài khoản muse đã hết hạn (thường vài ngày) hoặc hết hạn mức tuần | Vào Muse2API, **thêm lại tài khoản** muse của bạn (Bước 1 mục 4); hạn mức tuần sẽ tự hồi theo lịch của muse.ai |
| Tạo **ảnh** khóa cho nhân vật người thật bị từ chối | Công cụ tạo ảnh của muse không nhận ảnh người thật làm khung khóa | Dùng chế độ **Người thật** (quay thẳng video + ảnh mẫu) thay cho chế độ PRO khi làm phim người thật |
| Các cảnh trong phim bị **trùng một clip** cho nhiều cảnh | Đã dùng chế độ chạy "đồng bộ/coherent" cho cả tập phim | Làm phim luôn dùng chế độ **độc lập (independent)** — bản Studio trong repo này đã mặc định như vậy, đừng đổi |
| Phim dựng xong nhưng không có tiếng | ffmpeg chưa đúng chỗ hoặc film-service chưa chạy khi dựng | Kiểm tra đủ `ffmpeg.exe` + `ffprobe.exe` ở `C:\muse2api-test\ffmpeg\bin` (Bước 2) và `/health` (Bước 4), rồi dựng lại |
| Phim xong nhưng không thấy ở đâu | — | Mở Studio → **Thư viện** → kéo xuống mục **🎬 Phim đã hoàn thành**; hoặc mở thư mục `film-service\outputs` |

## Bảo mật cho chính bạn

- File **`.env`**, thư mục **`data`** của Muse2API và cookie đăng nhập chứa toàn bộ quyền truy cập tài khoản muse của bạn. **Không gửi, không chia sẻ, không đăng lên mạng** — kể cả "gửi để người ta xem lỗi hộ". Xem lỗi thì chụp màn hình che phần key đi.
- Cả Muse2API và film-service chỉ chạy ở `127.0.0.1` (ngay trên máy bạn), không ai từ Internet truy cập được trừ khi bạn tự mở cổng — đừng mở.
- Đổi API key nếu nghi ngờ đã lộ: xóa/đổi dòng `KEY=` trong `.env` rồi khởi động lại Muse2API và mở lại Studio bằng địa chỉ có key mới.

## Cấu trúc repo này

```
muse-studio/
├─ README.md                  ← file hướng dẫn bạn đang đọc
├─ LICENSE                    ← giấy phép MIT cho phần Studio + film-service
├─ studio/
│  └─ studio.html             ← giao diện Muse Studio (đổi tên thành batch.html khi cài)
├─ film-service/
│  ├─ film_service.py         ← dịch vụ lồng tiếng + nhạc nền + dựng phim (cổng 18621)
│  └─ synth_vieneu.py         ← cầu nối VieNeu-TTS (đặt vào thư mục tts-pro khi dùng)
└─ images/
   └─ muse-studio-thu-vien.png ← ảnh chụp giao diện thật
```

Sau khi cài xong, cấu trúc trên máy của bạn sẽ là:

```
C:\muse2api-test\
├─ app\Muse2API_VI_Portable_1.6.8\   ← Muse2API + batch.html (chính là studio.html)
├─ ffmpeg\bin\                       ← ffmpeg.exe + ffprobe.exe
├─ film-service\                     ← film_service.py, outputs\ (phim thành phẩm)
└─ tts-pro\                          ← (tuỳ chọn) VieNeu-TTS + synth_vieneu.py + model\
```

## Vài lưu ý quan trọng trước khi dùng

- Muốn **đổi chữ ký mặc định trên phim** thành tên của bạn: mở `studio.html` tìm chữ `by prompt Thaovy19T` và sửa thành chữ ký của bạn (chỉ 1 chỗ); trong `film_service.py` cũng có giá trị mặc định tương tự ở dòng `signature = payload.get(...)`. Đây là chữ ký của tác giả bản Studio này — tôn trọng bản quyền thì giữ cũng tốt, không bắt buộc.
- **Không** dùng chế độ *đồng bộ/coherent* để quay cả tập phim (sẽ trùng clip). Làm phim nhiều cảnh luôn quay **độc lập**.
- Phim người thật: dùng chế độ **Người thật**. Phim thú/hoạt hình: dùng **PRO**.
- Mỗi cảnh quay tối đa 10 giây — hãy chia kịch bản thành nhiều cảnh ngắn thay vì một cảnh dài.

## Ghi nhận & giấy phép

- **Muse Studio (giao diện `studio.html`) + film-service**: phát hành theo giấy phép **MIT** (xem file `LICENSE`) bởi Thaovy19T — bạn được dùng, sửa, chia sẻ lại miễn phí, chỉ cần giữ ghi nhận tác giả. Nếu bản này giúp bạn đỡ bị lừa mất tiền oan, vậy là đạt mục đích rồi.
- **Muse2API** (động cơ tạo ảnh/video): dự án độc lập tại https://github.com/bitgacon/muse2api, giấy phép MIT, phát triển từ `bynne2602/muse2api`, dựa trên `czg86389-hub/muse2api`. Repo này không sở hữu và không phân phối lại động cơ đó.
- **VieNeu-TTS**: dự án lồng tiếng Việt độc lập của tác giả của nó, repo này chỉ chứa file cầu nối `synth_vieneu.py`.
- **muse.ai / Muse** là dịch vụ của bên thứ ba. Muse2API là cầu nối **không chính thức** tới dịch vụ đó — không liên kết với Meta hay nhà cung cấp muse.ai. Hãy dùng bằng tài khoản của chính bạn, tuân thủ điều khoản của muse.ai; việc tự động hoá có thể bị dịch vụ giới hạn theo chính sách của họ, và đó là quyết định/rủi ro của mỗi người dùng.

---

*Chúc bạn làm được nhiều bộ phim hay — miễn phí, tự tay làm, không mất tiền oan cho ai cả.*

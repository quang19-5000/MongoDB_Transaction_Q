1, mongodb_transaction(tt): giao tác tập trung

Quản lý tài khoản ngân hàng và thực hiện giao dịch chuyển tiền trong cùng một cơ sở dữ liệu MongoDB

a, Kết nối với MongoDB:

MongoClient được sử dụng để tạo kết nối đến MongoDB thông qua URI được cung cấp trong MONGO_URI.

Cơ sở dữ liệu có tên "bank" và collection "accounts" được truy cập để lưu thông tin tài khoản.

b, Chức năng check_balance:

Dùng để kiểm tra số dư tài khoản của một người dùng, dựa vào _id của họ trong collection accounts.

Nếu tài khoản tồn tại, hàm sẽ in ra số dư, ngược lại sẽ thông báo tài khoản không tồn tại.

c, Chức năng transfer_money:

Thực hiện chuyển tiền giữa hai tài khoản trong cùng một collection, với cơ chế bảo đảm dữ liệu nhất quán thông qua giao dịch (transaction).

Các bước chính:

Giảm tiền từ tài khoản người gửi (sender), nhưng chỉ khi họ có đủ tiền (kiểm tra bằng điều kiện balance >= amount).

Tăng tiền vào tài khoản người nhận (receiver).

Giao dịch thành công nếu cả hai bước trên đều được thực hiện thành công, sau đó commit transaction.

Nếu xảy ra bất kỳ lỗi nào trong quá trình này, giao dịch sẽ bị hủy (rollback) để đảm bảo dữ liệu không bị sai lệch.

d, Chạy kiểm tra và thực hiện giao dịch:

Trước khi giao dịch, số dư của hai tài khoản (user_A và user_B) được kiểm tra và in ra.

Giao dịch được thực hiện thông qua hàm transfer_money, chuyển 300 VND từ user_B sang user_A.

Sau khi giao dịch, số dư của hai tài khoản được kiểm tra lại để xác nhận thay đổi.

e, Đóng kết nối:

Sau khi hoàn tất, kết nối với MongoDB được đóng bằng client.close().


2, mongodb_transaction(pt): giao tác phân tán

Mục đích chính là thực hiện các giao dịch tài chính giữa hai cơ sở dữ liệu MongoDB khác nhau, đồng thời đảm bảo tính toàn vẹn dữ liệu thông qua cơ chế giao dịch (transaction)

a, Kết nối với hai MongoDB database
Hai URI (MONGO_URI_DB1 và MONGO_URI_DB2) được sử dụng để kết nối đến hai cơ sở dữ liệu MongoDB riêng biệt.

Sử dụng MongoClient để tạo các client tương ứng với từng database (client_db1 và client_db2).

b, Chọn database và collection
db1 đại diện cho cơ sở dữ liệu "bank1" và collection "accounts" trong database này.

db2 tương tự, đại diện cho "bank2".

c, Hàm setup_users
Mục đích:

Tạo tài khoản người dùng nếu chưa tồn tại trong hai database.

Dữ liệu mẫu:

user_A trong accounts_db1 với số dư 1000.

user_B trong accounts_db2 với số dư 500.

Sử dụng count_documents để kiểm tra tài khoản có tồn tại hay không trước khi insert_one.

d, Hàm transfer_money
Giao dịch giữa hai database:

Giao dịch được thực hiện trong cùng lúc với cả người gửi (sender) và người nhận (receiver), mỗi người nằm trong một database khác nhau.

Các bước chính:

Kiểm tra số dư người gửi (sender): Phải đảm bảo số tiền đủ lớn để thực hiện giao dịch.

Kiểm tra tài khoản người nhận (receiver): Người nhận phải tồn tại trong cơ sở dữ liệu tương ứng.

Trừ tiền từ tài khoản người gửi.

Cộng tiền vào tài khoản người nhận.

Cơ chế rollback:

Nếu xảy ra bất kỳ lỗi nào trong quá trình giao dịch (ví dụ, không tìm thấy tài khoản hoặc số dư không đủ), cả hai giao dịch trong hai database sẽ bị hoàn tác (rollback) để duy trì tính toàn vẹn dữ liệu.

e, Chạy chương trình chính (__main__)
Tạo hai người dùng bằng cách gọi setup_users.

Thực hiện giao dịch:

Chuyển 300 từ user_A (trong db1) sang user_B (trong db2).

Chuyển 1500 từ user_B (trong db2) sang user_A (trong db1) (hiện tại dòng này bị chú thích, bạn có thể bỏ chú thích để thử nghiệm).

In dữ liệu sau giao dịch:

Lấy danh sách tất cả các tài khoản trong cả hai database để hiển thị số dư mới.

Đóng kết nối với MongoDB bằng client_db1.close() và client_db2.close().

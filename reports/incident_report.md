# Incident Report

## Severity
**P1 / High** (Ảnh hưởng trực tiếp đến CEO Dashboard và Doanh thu ghi nhận)

## Summary
Vào lúc 10:37 AM (theo giờ test), hệ thống ghi nhận sự sụt giảm nghiêm trọng về khối lượng dữ liệu đơn hàng (volume drop). Chỉ có 150 dòng dữ liệu được ingest thành công thay vì mức thông thường là ~600 dòng. Sự cố này không làm thay đổi schema của dữ liệu nên đã lọt qua lớp Contract Validation, nhưng bị hệ thống Anomaly Detection (thuật toán MAD) phát hiện.

## Detection
- **Signal:** `row-count anomaly = True` (Phương pháp: `auto:mad:weekend`, Score: 5.53)
- **First observed time:** Ghi nhận ngay sau khi chạy `make baseline` đợt ingest mới nhất.

## Root Cause
Lỗi ở tầng Ingestion (Partial Ingestion Fault). Job tải dữ liệu (extractor) hoặc hệ thống upstream chỉ gửi 25% (150/600) lượng đơn hàng thực tế vào hệ thống, khiến dữ liệu bị thiếu hụt nghiêm trọng.

## Evidence
1. **Contract Validation**: Báo cáo `contract failed checks = 0`. Điều này chứng minh dữ liệu đến không bị sai định dạng, sai kiểu hay null.
2. **Row Count**: `orders rows = 150` (Giảm 75% so với mức ~600 orders thông thường).
3. **Anomaly Score**: Hệ thống Anomaly trả về `True` với score = 5.53 (vượt xa ngưỡng an toàn threshold=3.0).

## Blast Radius

```text
stg_orders
 -> fct_daily_revenue
    -> ceo_revenue_dashboard
```
Sự cố khiến Dashboard của CEO sẽ hiển thị doanh thu ngày hôm nay thấp hơn 75% so với thực tế, gây báo động giả (false alarm) về tình hình kinh doanh.

## Mitigation
- Tạm dừng luồng chạy dbt (Pause dbt pipeline) để không đẩy dữ liệu thiếu hụt (150 rows) lên ghi đè bảng `fct_daily_revenue`.
- Cô lập (Quarantine) batch dữ liệu lỗi này.
- Báo cáo cho đội upstream/ingestion để chạy lại (backfill) toàn bộ batch dữ liệu ngày hôm nay.

## Recovery
Chạy lại script reset/backfill từ nguồn đúng:
```bash
make reset
make baseline
```

## Verification
- [x] Contract healthy
- [x] dbt tests healthy
- [x] anomaly returned to expected range (Số lượng dòng quay về mức ~600)
- [x] SLO healthy / budget understood
- [x] downstream output verified

## Prevention / Action Items
| Action | Owner | Deadline | Why |
|---|---|---|---|
| Bổ sung Volume/Row Count vào Data Contract (Data SLA) | Data Engineer | ASAP | Chặn dữ liệu thiếu hụt ngay từ cửa, trước khi vào dbt |
| Thiết lập Alert PagerDuty cho Anomaly Detector | SRE / Ops | Tuần tới | Tự động gọi điện/nhắn tin cho on-call khi MAD score > 3 |
| Bật tính năng dbt build fail-fast nếu row_count bất thường | Analytics Eng | Tuần tới | Tránh làm sai lệch CEO Dashboard |

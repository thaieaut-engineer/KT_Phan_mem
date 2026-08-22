-- =========================================================
-- PETSHOP SAMPLE DATA
-- =========================================================

-- =========================================================
-- USERS
-- =========================================================

INSERT INTO users
(username, email, password, full_name, phone, address, role, status)
VALUES
(
    'admin',
    'admin@petshop.com',
    '123456',
    'Quản trị viên',
    '0900000000',
    'Hà Nội',
    'admin',
    1
),
(
    'customer01',
    'customer01@gmail.com',
    '123456',
    'Nguyễn Văn An',
    '0911111111',
    'Hà Nội',
    'customer',
    1
),
(
    'customer02',
    'customer02@gmail.com',
    '123456',
    'Trần Thị Bình',
    '0922222222',
    'Hồ Chí Minh',
    'customer',
    1
);


-- =========================================================
-- CATEGORIES
-- =========================================================

INSERT INTO categories
(name, description, status)
VALUES
(
    'Thức ăn cho chó',
    'Các loại thức ăn dành cho chó',
    1
),
(
    'Thức ăn cho mèo',
    'Các loại thức ăn dành cho mèo',
    1
),
(
    'Đồ chơi thú cưng',
    'Đồ chơi dành cho chó và mèo',
    1
),
(
    'Phụ kiện',
    'Dây dắt, vòng cổ, quần áo và phụ kiện',
    1
),
(
    'Chăm sóc thú cưng',
    'Các sản phẩm vệ sinh và chăm sóc',
    1
),
(
    'Chuồng và nhà',
    'Chuồng, nhà và ổ nằm cho thú cưng',
    1
);


-- =========================================================
-- PRODUCTS
-- =========================================================

INSERT INTO products
(category_id, name, description, price, sale_price, stock, image, status)
VALUES

-- DOG FOOD

(
    1,
    'Royal Canin Adult Dog',
    'Thức ăn cao cấp dành cho chó trưởng thành',
    450000,
    399000,
    30,
    NULL,
    'active'
),

(
    1,
    'Pedigree Adult',
    'Thức ăn dinh dưỡng cho chó trưởng thành',
    250000,
    220000,
    25,
    NULL,
    'active'
),

(
    1,
    'SmartHeart Puppy',
    'Thức ăn dành cho chó con',
    190000,
    175000,
    30,
    NULL,
    'active'
),

(
    1,
    'Ganador Premium',
    'Thức ăn chất lượng cao cho chó',
    210000,
    195000,
    25,
    NULL,
    'active'
),

(
    1,
    'ANF 6 Free Dog',
    'Thức ăn cao cấp cho chó',
    520000,
    490000,
    20,
    NULL,
    'active'
),


-- CAT FOOD

(
    2,
    'Me-O Tuna',
    'Thức ăn vị cá ngừ cho mèo',
    180000,
    165000,
    40,
    NULL,
    'active'
),

(
    2,
    'Whiskas Adult',
    'Thức ăn dành cho mèo trưởng thành',
    220000,
    200000,
    35,
    NULL,
    'active'
),

(
    2,
    'Royal Canin Kitten',
    'Thức ăn dành cho mèo con',
    420000,
    399000,
    25,
    NULL,
    'active'
),

(
    2,
    'Cat Eye Tuna',
    'Thức ăn vị cá ngừ cho mèo',
    160000,
    145000,
    40,
    NULL,
    'active'
),

(
    2,
    'Nekko Pouch',
    'Pate dinh dưỡng cho mèo',
    35000,
    NULL,
    100,
    NULL,
    'active'
),


-- TOYS

(
    3,
    'Bóng cao su cho chó',
    'Bóng đồ chơi cao su an toàn cho chó',
    85000,
    75000,
    50,
    NULL,
    'active'
),

(
    3,
    'Chuột đồ chơi cho mèo',
    'Đồ chơi hình chuột dành cho mèo',
    35000,
    NULL,
    50,
    NULL,
    'active'
),

(
    3,
    'Bóng len cho mèo',
    'Bóng len nhiều màu sắc',
    25000,
    NULL,
    60,
    NULL,
    'active'
),

(
    3,
    'Dây thừng đồ chơi',
    'Đồ chơi dây thừng giúp chó vận động',
    65000,
    55000,
    40,
    NULL,
    'active'
),


-- ACCESSORIES

(
    4,
    'Dây dắt chó',
    'Dây dắt chắc chắn dành cho chó',
    180000,
    160000,
    20,
    NULL,
    'active'
),

(
    4,
    'Vòng cổ thú cưng',
    'Vòng cổ nhiều kích thước',
    90000,
    79000,
    30,
    NULL,
    'active'
),

(
    4,
    'Áo cho chó',
    'Áo thời trang dành cho thú cưng',
    220000,
    199000,
    15,
    NULL,
    'active'
),

(
    4,
    'Balo vận chuyển thú cưng',
    'Balo tiện lợi khi đưa thú cưng đi xa',
    450000,
    420000,
    8,
    NULL,
    'active'
),


-- CARE

(
    5,
    'Dung dịch vệ sinh tai',
    'Dung dịch vệ sinh tai cho thú cưng',
    130000,
    NULL,
    30,
    NULL,
    'active'
),

(
    5,
    'Khăn lau thú cưng',
    'Khăn mềm chuyên dụng cho thú cưng',
    70000,
    59000,
    45,
    NULL,
    'active'
),

(
    5,
    'Sữa tắm chó mèo',
    'Sữa tắm dịu nhẹ cho thú cưng',
    150000,
    135000,
    35,
    NULL,
    'active'
),

(
    5,
    'Lược chải lông',
    'Lược chải lông cho chó mèo',
    85000,
    75000,
    25,
    NULL,
    'active'
),


-- HOUSE

(
    6,
    'Ổ nằm cho chó',
    'Ổ nằm mềm mại dành cho chó',
    350000,
    320000,
    12,
    NULL,
    'active'
),

(
    6,
    'Nhà nhựa cho mèo',
    'Nhà nhựa dành cho mèo',
    550000,
    NULL,
    10,
    NULL,
    'active'
),

(
    6,
    'Đệm nằm thú cưng',
    'Đệm mềm mại cho chó và mèo',
    280000,
    250000,
    20,
    NULL,
    'active'
),

(
    6,
    'Chuồng thú cưng',
    'Chuồng chắc chắn dành cho chó mèo',
    850000,
    799000,
    8,
    NULL,
    'active'
);
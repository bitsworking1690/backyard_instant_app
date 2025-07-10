// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs

Table users {
  id int [pk, increment]
  uuid varchar(255) [unique]
  title varchar(255)
  first_name int
  last_name timestamp
  email varchar(255)
  mobile varchar(255)
  role varchar(255)
  otp int
  otp_expiry_at timestamp
  password varchar(255)
  is_active bool
  created_at timestamp
  updated_at timestamp
}

Table roles {
  id int [pk, increment]
  name varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table user_roles {
  id int [pk, increment]
  user_id int [unique, ref: > users.id]
  role_id int [unique, ref: > roles.id]
  created_at timestamp
  updated_at timestamp
}

Table permissions {
  id int [pk, increment]
  name varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table role_permissions {
  id int [pk, increment]
  role_id int [ref: > roles.id]
  permission_id int [ref: > permissions.id]
  created_at timestamp
  updated_at timestamp
}

Table categories {
  id int [pk, increment]
  name varchar(255)
  type varchar(255)
  is_active boolean
}

Table templates {
  id int [pk, increment]
  name varchar(255)
  category_id int [ref: > categories.id]
  is_paid boolean
  discount decimal(5, 2)
  price decimal(10, 2)
  source_code text
  is_active boolean
}

Table wishlist {
  id int [pk, increment]
  template_id int [ref: > templates.id]
  user_id int [ref: > users.id]
  created_at timestamp
}

Table custom_templates {
  id int [pk, increment]
  event_id int [ref: - events.id]
  template_id int [ref: > templates.id]
  name1 varchar(255)
  name2 varchar(255)
  headline varchar(255)
  headline_font_size int
  sub_headline varchar(255)
  sub_headline_font_size int
  date date
  time time
  venue_name varchar(255)
  text_under_barcode varchar(255)
  width int
  height int
  created_at timestamp
  updated_at timestamp
}


Table events {
  id int [pk, increment]
  name varchar(255)
  type varchar(255)
  market_status varchar(255)
  description text
  user_id int [ref: > users.id]
  template_id int [ref: > templates.id]
  is_custom_template boolean
  guests int
  tbd boolean
  start_date date
  end_date date
  start_time time
  end_time time
  timezone varchar(255)
  address varchar(255)
  latitude decimal(10, 8)
  longitude decimal(11, 8)
  status varchar(255)
  created_at timestamp
  updated_at timestamp
}

Enum invitation_types  {
  pending
  accepted
  declined
}
Table invitations {
  id int [pk, increment]
  event_id int [ref: > events.id]
  user_id int [ref: > users.id]
  ticket_type varchar(255)
  ticket_no varchar(255)
  barcode varchar(255)
  checkin datetime
  checkout datetime
  status invitation_types
  actioned_datetime datetime
  coupon_id int [ref: - coupons.id]
  coupon_discount decimal(10, 2)
  created_at timestamp
  updated_at timestamp
}

Table event_zones {
  id int [pk, increment, ref: < coupon_zones.zone_id]
  event_id int [ref: > events.id]
  name varchar(255)
  capacity int
  type varchar(255)
  color varchar(255)
  created_at timestamp
  updated_at timestamp
}


Table tickets {
  id int pk
  event_id varchar(255)
  name varchar(255)
  description varchar(255)
  price decimal
  discount decimal
  quantity int
  type varchar(255)
  date date
  timezone varchar(255)
  start_time time
  end_time time
  no_of_entries int
  color varchar(255)
  created_at timestamp
  updated_at timestamp
}

Table ticket_zones {
  id int [pk, increment]
  ticket_id int [ref: > tickets.id]
  zone_id int [ref: > event_zones.id]
}

Table coupons {
  id int [PK, increment, ref: < coupon_zones.coupon_id] 
  event_id varchar(255)
  name varchar(255)
  code varchar(255)
  discount_type varchar(255)
  discount decimal
  usage int
  ticket_type varchar(255)
  start_date date
  end_date date
  timezone varchar(255)
  start_time time
  end_time time
  until_sold_out boolean
  created_at timestamp
  updated_at timestamp
}

Table coupon_zones {
  id int [pk, increment]
  coupon_id int
  zone_id int
}
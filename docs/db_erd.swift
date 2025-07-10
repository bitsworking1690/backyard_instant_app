// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs


// Accounts-Auth-Users Management //
Table User {
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

  is_active boolean
  created_at timestamp
  updated_at timestamp
}

Table Role {
  id int [pk, increment]
  name varchar(255)

  is_active boolean
  created_at timestamp
  updated_at timestamp
}

Table UserRole {
  id int [pk, increment]
  user_id int [unique, ref: > User.id]
  role_id int [unique, ref: > Role.id]

  is_active boolean
  created_at timestamp
  updated_at timestamp
}

Table Permission {
  id int [pk, increment]
  name varchar(255)

  is_active boolean
  created_at timestamp
  updated_at timestamp
}

Table RolePermission {
  id int [pk, increment]
  role_id int [ref: > Role.id]
  permission_id int [ref: > Permission.id]

  is_active boolean
  created_at timestamp
  updated_at timestamp
}

// User Settings Management //
Table UserSetting {
  id integer [pk, increment]
  user_id integer [ref: > User.id] // User associated with the setting
  key varchar // Setting key (e.g., "notification_preference", "language")
  value json // Setting value (can store different data types)
  description text // Optional description of the setting
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Modules Management //
Table Module {
  id int [pk, increment]
  name varchar(255) // Name of the module (e.g., "Event", "LMS", "CMS")
  description text // Detailed description of the module
  is_active boolean // Whether the module is active or not
  created_at timestamp
  updated_at timestamp
}

Table ClientModule {
  id int [pk, increment]
  client_id int [ref: > Client.id] // Client using the module
  module_id int [ref: > Module.id] // Associated module
  
  is_active boolean // Whether the module is active for the client
  created_at timestamp
  updated_at timestamp
}

Table EventModule {
  id int [pk, increment]
  event_id int [ref: > Event.id] // Associated event
  module_id int [ref: > Module.id] // Module used in the event
  is_active boolean // Whether the module is active for the event
  created_at timestamp
  updated_at timestamp
}

// Form Builder Management //
Table Form {
  id integer [pk]
  title varchar
  description text
  module_id integer [ref: > Module.id]
  created_by integer [ref: > User.id] // Admin or Client who created the form
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Enum FieldTypes  {
  text 
  number
  datetime 
  dropdown 
  checkbox 
  radio 
  file
}

Table FormField {
  id integer [pk]
  form_id integer [ref: > Form.id]
  field_type FieldTypes
  label varchar
  placeholder varchar
  is_required bool
  options json // For dropdown, checkbox, and radio fields
  order integer // To arrange fields in the form
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table FormSubmission {
  id integer [pk]
  form_id integer [ref: > Form.id]
  module_id integer [ref: > Module.id]
  submitted_by integer [ref: > User.id] // User who submitted the form
  submission_data json // Stores all field responses
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Enum Status  {
  pending
  completed
}

Table FormAssignment {
  id integer [pk]
  form_id integer [ref: > Form.id]
  assigned_to integer [ref: > User.id] // User assigned to fill the form
  assigned_by integer [ref: > User.id] // Admin or Client who assigned the form
  status  Status
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Enum EventStatus  {
  upcoming
  ongoing
  completed
}

// Events Management //
Table Event {
  id integer [pk]
  title varchar
  description text
  start_date datetime
  end_date datetime
  rules text
  prizes text
  registration_form_id integer [ref: > Form.id] // Dynamic form for registration
  status EventStatus
  created_by integer [ref: > User.id]
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Team {
  id integer [pk]
  name varchar
  event_id integer [ref: > Event.id]
  leader_id integer [ref: > User.id] // Participant who created the team
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table TeamMember {
  id integer [pk]
  team_id integer [ref: > Team.id]
  user_id integer [ref: > User.id] // Participant joining the team
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Submission {
  id integer [pk]
  event_id integer [ref: > Event.id]
  team_id integer [ref: > Team.id]
  submission_file file
  submission_link varchar
  description text
  submitted_by integer [ref: > User.id] // Participant who submitted
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table EvaluationCriteria {
  id integer [pk]
  event_id integer [ref: > Event.id]
  criteria_name varchar
  criteria_description varchar
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table EvaluationCriteriaItems {
  id integer [pk]
  criteria_id integer [ref: > EvaluationCriteria.id]
  criteria_title varchar
  criteria_description varchar
  weight float
  percentage float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table EvaluationCriteriaItemScore {
  id integer [pk]
  criteria_id integer [ref: > EvaluationCriteria.id]
  criteria_item_id integer [ref: > EvaluationCriteriaItems.id]
  taken_score float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table JudgeAssignment {
  id integer [pk]
  event_id integer [ref: > Event.id]
  judge_id integer [ref: > User.id] // User with role 'judge'
  submission_id integer [ref: > Submission.id]
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Evaluation {
  id integer [pk]
  submission_id integer [ref: > Submission.id]
  judge_id integer [ref: > User.id]
  criteria_id integer [ref: > EvaluationCriteria.id]
  score float
  feedback text
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Registration {
  id integer [pk]
  event_id integer [ref: > Event.id]
  user_id integer [ref: > User.id] // Participant registering
  status Status // [pending, approved, rejected]
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// LearningHub-Mini-LMS Management //
Table Course {
  id integer [pk]
  title varchar
  description text
  enrollment_form_id integer [ref: > Form.id] // Dynamic form for enrollment
  created_by integer [ref: > User.id]
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Class {
  id integer [pk]
  course_id integer [ref: > Course.id]
  title varchar
  description text
  teacher_id integer [ref: > User.id] // User with role 'teacher'
  schedule datetime // For live classes
  recording_link varchar // For recorded classes
  materials file // Slides, PDFs, etc.
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Enum CourseStatus  {
  pending
  completed
  approved
}

Table Enrollment {
  id integer [pk]
  course_id integer [ref: > Course.id]
  user_id integer [ref: > User.id] // Participant enrolling
  status CourseStatus
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Assignment {
  id integer [pk]
  class_id integer [ref: > Class.id]
  title varchar
  description text
  deadline datetime
  max_score float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table AssignmentSubmission {
  id integer [pk]
  assignment_id integer [ref: > Assignment.id]
  user_id integer [ref: > User.id] // Participant submitting
  submission_file file
  submission_link varchar
  feedback text
  score float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Quiz {
  id integer [pk]
  class_id integer [ref: > Class.id]
  title varchar
  description text
  max_score float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table QuizSubmission {
  id integer [pk]
  quiz_id integer [ref: > Quiz.id]
  user_id integer [ref: > User.id] // Participant submitting
  answers json // Store quiz answers
  feedback text
  score float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Certificate {
  id integer [pk]
  user_id integer [ref: > User.id] // Participant receiving the certificate
  course_id integer [ref: > Course.id]
  certificate_file file
  issued_by integer [ref: > User.id] // Admin or Teacher issuing the certificate
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Shared Models/Services //
Table Notification {
  id integer [pk, increment]
  user_id integer [ref: > User.id] // Recipient
  title varchar // Notification title
  message text // Notification message
  type varchar // e.g., "info", "warning", "error", "success"
  platform varchar // e.g., "web", "mobile", "both"
  is_read bool // Whether the notification has been read
  metadata json // Additional data (e.g., links, actions, etc.)
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Analytics {
  id integer [pk, increment]
  system_id integer [null] // For system-wide analytics
  client_id integer [ref: > Client.id, null] // For client-specific analytics
  module_id integer [ref: > Module.id, null] // For module-specific analytics
  event_id integer [ref: > Event.id, null] // For hackathon-specific analytics
  course_id integer [ref: > Course.id, null] // For course-specific analytics
  metric_name varchar // e.g., "participant_count", "submission_count"
  metric_value float
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// CMS Managements //
Table PageCategory {
  id integer [pk, increment]
  name varchar // Category name
  description text // Optional description of the category
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Page {
  id integer [pk, increment]
  title varchar
  slug varchar [unique]
  content text // Rich text for rendering the page
  parent_id integer [ref: > Page.id, null] // Self-referencing for parent-child hierarchy
  category integer [ref: > PageCategory.id, null] // e.g., "home", "about", "contact", etc.
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// FAQ Management //
Table FAQ {
  id integer [pk, increment]
  question text
  answer text
  category varchar // e.g., "General", "Technical", etc.
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Knowledge Base Management //
Table KnowledgeBase {
  id integer [pk, increment]
  title varchar
  content text // Detailed article content
  category varchar // e.g., "Getting Started", "Troubleshooting", etc.
  tags json // List of tags for search and filtering
  created_by integer [ref: > User.id] // Author of the article
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table KnowledgeBaseCategory {
  id integer [pk, increment]
  name varchar // Category name
  description text // Optional description of the category
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table KnowledgeBaseTag {
  id integer [pk, increment]
  name varchar // Tag name
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Support Data Management //
Table SupportTicket {
  id integer [pk, increment]
  user_id integer [ref: > User.id] // User who created the ticket
  subject varchar
  description text
  status varchar // e.g., "open", "in_progress", "resolved", "closed"
  priority varchar // e.g., "low", "medium", "high", "urgent"
  zone_id integer [ref: > Zone.id] // Zone related to the ticket
  category_id integer [ref: > SupportCategory.id] // Category of the ticket
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table SupportStaffAssignment {
  id integer [pk, increment]
  ticket_id integer [ref: > SupportTicket.id] // Ticket assigned
  staff_id integer [ref: > User.id] // Support staff assigned to the ticket
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table SupportTicketResponse {
  id integer [pk, increment]
  ticket_id integer [ref: > SupportTicket.id] // Ticket being responded to
  responder_id integer [ref: > User.id] // User or staff responding
  message text
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table Zone {
  id integer [pk, increment]
  name varchar // Name of the zone
  description text // Optional description of the zone
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table SupportCategory {
  id integer [pk, increment]
  name varchar // Name of the category
  description text // Optional description of the category
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Onsite Chat Messaging //
Table ChatRoom {
  id integer [pk, increment]
  name varchar // Optional name for the chat room
  created_by integer [ref: > User.id] // User who created the chat room
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table ChatRoomParticipant {
  id integer [pk, increment]
  chat_room_id integer [ref: > ChatRoom.id]
  user_id integer [ref: > User.id] // Participant in the chat room
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table ChatMessage {
  id integer [pk, increment]
  chat_room_id integer [ref: > ChatRoom.id]
  sender_id integer [ref: > User.id] // User who sent the message
  message text // Message content
  message_type varchar // e.g., "text", "image", "file"
  attachment json // Optional attachment details (e.g., file URL, metadata)
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table ChatMessageStatus {
  id integer [pk, increment]
  message_id integer [ref: > ChatMessage.id]
  user_id integer [ref: > User.id] // User who read or received the message
  status varchar // e.g., "sent", "delivered", "read"
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// White Label Management //
Table Client {
  id integer [pk, increment]
  name varchar // Client name
  domain varchar [unique] // Client-specific domain
  logo file // Client logo
  theme json // Theme settings (e.g., colors, fonts)
  is_active bool
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table ClientUser {
  id integer [pk, increment]
  client_id integer [ref: > Client.id] // Associated client
  user_id integer [ref: > User.id] // User belonging to the client
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// System Settings //
Table SystemSetting {
  id integer [pk, increment]
  key varchar [unique] // Setting key (e.g., "site_name", "default_language")
  value json // Setting value (can store different data types)
  description text // Optional description of the setting
  scope varchar // Scope of the setting (e.g., "system", "client")
  client_id integer [ref: > Client.id, null] // Null for system-wide settings, client-specific otherwise
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// SaaS System Settings //
Table SaaSPlan {
  id integer [pk, increment]
  name varchar // Plan name (e.g., "Basic", "Pro", "Enterprise")
  description text // Description of the plan
  price float // Monthly or yearly price
  features json // List of features included in the plan
  is_active bool
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table SaaSSubscription {
  id integer [pk, increment]
  client_id integer [ref: > Client.id] // Client subscribing to the plan
  plan_id integer [ref: > SaaSPlan.id] // Subscribed plan
  start_date datetime // Subscription start date
  end_date datetime // Subscription end date
  status varchar // e.g., "active", "expired", "canceled"
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table SaaSInvoice {
  id integer [pk, increment]
  subscription_id integer [ref: > SaaSSubscription.id] // Related subscription
  invoice_number varchar [unique] // Unique invoice number
  amount float // Invoice amount
  status varchar // e.g., "paid", "unpaid", "overdue"
  issued_date datetime // Date the invoice was issued
  due_date datetime // Payment due date
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

// Data Import & Export Management //
Table DataImport {
  id integer [pk, increment]
  user_id integer [ref: > User.id] // User initiating the import
  file_name varchar // Name of the imported file
  file_type varchar // Type of the file (e.g., "csv", "json", "xml")
  status varchar // e.g., "pending", "in_progress", "completed", "failed"
  error_message text // Error details if the import fails
  imported_at datetime // Timestamp when the import was completed
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table DataExport {
  id integer [pk, increment]
  user_id integer [ref: > User.id] // User initiating the export
  file_name varchar // Name of the exported file
  file_type varchar // Type of the file (e.g., "csv", "json", "xml")
  status varchar // e.g., "pending", "in_progress", "completed", "failed"
  error_message text // Error details if the export fails
  exported_at datetime // Timestamp when the export was completed
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table DataImportMapping {
  id integer [pk, increment]
  import_id integer [ref: > DataImport.id] // Related data import
  source_field varchar // Field name in the imported file
  target_field varchar // Corresponding field name in the system
  transformation_rules json // Rules for transforming the data (e.g., formatting, validation)
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

Table DataExportMapping {
  id integer [pk, increment]
  export_id integer [ref: > DataExport.id] // Related data export
  source_field varchar // Field name in the system
  target_field varchar // Corresponding field name in the exported file
  transformation_rules json // Rules for transforming the data (e.g., formatting, validation)
  
  is_deleted bool
  created_at datetime
  updated_at datetime
}

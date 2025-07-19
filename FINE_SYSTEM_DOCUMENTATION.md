# Library Management System - Fine System Implementation

## Overview
This document outlines the comprehensive fine system implemented for the Library Management System. The system automatically tracks and calculates fines for overdue books.

## How the Fine System Works

### 1. **Fine Record Creation (On Approval)**
When a librarian approves a borrow request:
- A fine record is created with initial amount = 0
- Due date is set to 14 days from approval date
- Borrow record is updated with due_date

**Endpoint:** Automatic (in `/api/notifications/{notif_id}/approve`)

### 2. **Fine Updates (On Login)**
When a user logs in:
- All overdue fines for that user are recalculated
- Fine amounts are updated based on current date vs due date
- Formula: `days_late × 100` (100 per day)

**Endpoint:** Automatic (in `/login`)

### 3. **Fine Validation (On Borrow Request)**
When a user requests to borrow a book:
- System updates all overdue fines first
- Checks if user has any unpaid fines
- Blocks new borrow requests if unpaid fines exist

**Endpoint:** Automatic (in `/api/borrow/request`)

### 4. **Fine Finalization (On Return)**
When a book is returned:
- Final fine amount is calculated based on actual return date
- Fine record is updated with final amount
- Borrow record is marked as returned

**Endpoint:** `/api/fines/finalize-on-return`

## API Endpoints

### Fine Management
- `GET /api/fines` - Get all fines with filters
- `GET /api/fines/{fine_id}` - Get specific fine
- `DELETE /api/fines/{fine_id}/delete` - Delete fine
- `POST /api/fines/{fine_id}/pay` - Mark fine as paid

### Fine Calculation & Updates
- `POST /api/fines/update-overdue` - Update overdue fines for user(s)
- `POST /api/fines/finalize-on-return` - Finalize fine on book return
- `GET /api/fines/user/{user_id}/total` - Get user's total unpaid fines
- `POST /api/fines/daily-update` - Daily update for all overdue fines

### Helper Functions
- `calculate_fine_amount(due_date, current_date)` - Calculate fine amount
- `calculate_due_date(approval_date, loan_period_days)` - Calculate due date

## Database Schema Changes

### Borrow Table
Added `due_date` field:
```sql
ALTER TABLE borrow ADD COLUMN due_date date;
```

### Fines Table
Uses existing schema with fields:
- `id` - Primary key
- `borrow_id` - Reference to borrow record
- `user_id` - Reference to user
- `amount` - Fine amount (numeric)
- `paid` - Payment status (boolean)
- `paid_date` - Date of payment
- `payment_method` - Payment method
- `reason` - Reason for fine
- `created_at` - Creation date

## Implementation Flow

### Book Approval Process
1. Librarian approves borrow request
2. System sets due_date (approval_date + 14 days)
3. Creates fine record with amount = 0
4. Updates borrow status to "approved"

### User Login Process
1. User logs in successfully
2. System calls `update_overdue_fines(user_id)`
3. Recalculates all overdue fines for user
4. Updates fine amounts in database

### New Borrow Request Process
1. User requests to borrow book
2. System updates overdue fines first
3. Checks for unpaid fines
4. Blocks request if unpaid fines exist
5. Allows request if no unpaid fines

### Book Return Process
1. User/Librarian marks book as returned
2. System calls `finalize_fine_on_return(borrow_id, return_date)`
3. Calculates final fine amount
4. Updates fine record with final amount
5. Updates borrow record with return_date

## Fine Calculation Rules

- **Loan Period:** 14 days from approval
- **Fine Rate:** 100 per day late
- **Calculation:** `max(0, (return_date - due_date).days * 100)`
- **Grace Period:** None (fine starts day 1 after due date)

## Automation Features

### Daily Updates
- Endpoint: `/api/fines/daily-update`
- Should be called by cron job daily
- Updates all overdue fines automatically

### Login Updates
- Automatic when user logs in
- Ensures fines are current before user interaction

### Borrow Validation
- Prevents borrowing with unpaid fines
- Encourages payment compliance

## Error Handling

- Login continues even if fine update fails
- Borrow requests continue if fine check fails (logged as error)
- Graceful handling of missing dates or records
- Detailed error messages for debugging

## Security Considerations

- Only librarians can approve/reject requests
- Users can only see their own fines
- Fine updates are automatic and cannot be manually manipulated
- Payment status can only be updated through payment endpoint

## Usage Examples

### Check User's Total Fines
```bash
GET /api/fines/user/123/total
```

### Pay a Fine
```bash
POST /api/fines/456/pay
Content-Type: application/json
{
  "payment_method": "credit_card"
}
```

### Daily Maintenance
```bash
POST /api/fines/daily-update
```

This comprehensive system ensures that fines are automatically calculated, updated, and enforced throughout the library management workflow.

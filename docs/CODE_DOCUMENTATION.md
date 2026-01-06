# Code Documentation Guide

This document provides an overview of the code documentation structure and key areas of the codebase.

## 📚 Documentation Structure

### Module-Level Docstrings

All major modules include comprehensive docstrings explaining:
- Purpose and functionality
- Key features
- Usage examples
- Important notes

**Documented Modules:**
- `products/models.py` - Product catalog models
- `orders/models.py` - Order management models
- `cart/models.py` - Shopping cart models
- `payment/views.py` - Checkout and payment processing
- `fitness_club/fitness_club/settings.py` - Django configuration

### Class-Level Documentation

Key model classes include detailed docstrings:
- **Product**: Three product types (physical/digital/service), inventory, tax calculation
- **Order**: Order lifecycle, status tracking, fulfillment methods
- **CartItem**: Shopping cart item management
- **PickupLocation**: Pickup location management

### Function Documentation

Important functions include docstrings explaining:
- Purpose and parameters
- Return values
- Usage examples
- Edge cases

**Key Functions:**
- `_calc_shipping()` - Shipping calculation logic
- `_get_cart_items()` - Cart item retrieval
- `checkout()` - Main checkout view
- `create_downloads_and_email()` - Digital download generation

## 🔍 Key Code Sections

### Product Management (`products/`)

**Models:**
- `Category`: Product categories
- `Product`: Main product model with three types
- `ProductImage`: Product image management

**Key Features:**
- Product type detection (physical/digital/service)
- Inventory management
- Tax calculation (GST/PST)
- Image handling with main image selection

**Documentation Location:**
- Module docstring in `products/models.py`
- Class docstrings for each model
- Property method docstrings (e.g., `main_image_url`, `is_physical`)

### Order Processing (`orders/`)

**Models:**
- `Order`: Main order model
- `OrderItem`: Order line items
- `PickupLocation`: Pickup locations
- `DigitalDownload`: Secure download links

**Key Features:**
- Order status tracking
- Shipping and pickup fulfillment
- Digital download generation
- Order history

**Documentation Location:**
- Module docstring in `orders/models.py`
- Service functions in `orders/services.py`
- Admin customizations in `orders/admin.py`

### Checkout Flow (`payment/`)

**Views:**
- `checkout()`: Main checkout view with conditional logic

**Key Features:**
- Shipping calculation
- Tax calculation
- Pickup location selection
- Simplified checkout for digital/service products

**Documentation Location:**
- Module docstring in `payment/views.py`
- Function docstrings for helper functions
- Inline comments for complex logic

### Shopping Cart (`cart/`)

**Models:**
- `CartItem`: Cart item model

**Key Features:**
- Persistent cart (database-backed)
- Quantity management
- Subtotal calculation

**Documentation Location:**
- Module docstring in `cart/models.py`
- Class docstring for CartItem model

## 📝 Code Comments

### Inline Comments

Important sections include inline comments explaining:
- Complex logic
- Business rules
- Edge cases
- Configuration options

**Example Locations:**
- Shipping calculation logic
- Product type detection
- Order status transitions
- Digital download expiry

### Section Headers

Code is organized with clear section headers:
```python
# =========================
#  PRODUCT
# =========================

# -------------------------
# Validation / sanity rules
# -------------------------
```

## 🎯 Documentation Best Practices

### What's Documented

1. **Module Purpose**: What the module does
2. **Key Features**: Main functionality
3. **Usage Examples**: How to use the code
4. **Configuration**: Important settings
5. **Edge Cases**: Special scenarios

### What's Not Documented

- Obvious code (self-explanatory)
- Standard Django patterns
- Simple getters/setters
- Standard CRUD operations

## 🔧 Adding New Documentation

When adding new code:

1. **Add module docstring** if creating a new module
2. **Add class docstring** for models and complex classes
3. **Add function docstring** for public functions
4. **Add inline comments** for complex logic
5. **Update this guide** if adding major features

### Docstring Format

```python
"""
Brief description.

Detailed explanation of purpose, features, and usage.

Key Features:
- Feature 1
- Feature 2

Usage Example:
    # Example code here
    result = function_call()
"""
```

## 📖 Reading the Code

### For Learning

1. Start with module docstrings
2. Read class docstrings
3. Review function docstrings
4. Check inline comments for details

### For Development

1. Check existing patterns
2. Follow documentation style
3. Add docstrings for new code
4. Update related documentation

## 🚀 Quick Reference

**Product Types:**
- Physical: `is_digital=False, is_service=False`
- Digital: `is_digital=True`
- Service: `is_service=True`

**Order Status:**
- `pending`: Order created, awaiting payment
- `paid`: Payment received
- `shipped`: Order shipped
- `delivered`: Order delivered
- `cancelled`: Order cancelled

**Checkout Types:**
- Physical products: Full checkout with shipping/pickup
- Digital/service only: Simplified checkout (order summary only)

**Shipping Logic:**
- Physical products: Flat rate or free over threshold
- Pickup orders: No shipping fee
- Digital/service: No shipping required

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Project Structure Guide](PROJECT_STRUCTURE.md)
- [Deployment Guide](AWS_DEPLOYMENT.md)
- [Main README](../README.md)

---

**Note**: This codebase is extensively documented for learning purposes. All major components include comprehensive documentation to help understand the implementation.


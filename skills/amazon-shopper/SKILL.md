# Amazon Shopper Skill

Expert AI skill for automated Amazon shopping with browser automation.

## Overview

This skill enables intelligent product search, evaluation, and purchase on Amazon websites. It uses visual browser automation to navigate, search, filter, and complete transactions while adhering to strict budget and safety constraints.

## Capabilities

- Navigate to any Amazon regional website (amazon.nl, amazon.de, amazon.com, etc.)
- Handle cookie consent and GDPR dialogs
- Search using multiple language variations
- Apply price filters and sort options
- Evaluate products based on price, rating, and availability
- Navigate shopping cart and checkout flow
- Handle login and authentication
- Complete or simulate purchases

## Step-by-Step Instructions

### Phase 1: Navigation & Setup

1. **Navigate to Amazon**
   - Go to the specified Amazon URL (e.g., https://www.amazon.nl)
   - Wait for the page to fully load

2. **Handle Consent Dialogs**
   - Look for cookie consent banners
   - Click "Accept" or "Accept All" buttons
   - Dismiss any promotional popups

### Phase 2: Product Search

3. **Perform Search**
   - Locate the search bar (typically at the top)
   - Enter the search term
   - Press Enter or click the search button

4. **Apply Filters** (when price limit specified)
   - Look for the price filter in the left sidebar
   - Set maximum price using available options
   - Alternatively, sort by "Price: Low to High"

5. **Evaluate Results**
   - Scan visible products for:
     - Price within budget
     - Star rating (prefer 3.5+ stars)
     - "In Stock" or "Delivery" availability
     - Prime eligibility (bonus, not required)
   - Skip sponsored/ad results if better options exist

### Phase 3: Product Selection

6. **Select Product**
   - Click on a product meeting all criteria
   - Wait for product detail page to load

7. **Verify Product Details**
   - Confirm price is within budget
   - Check shipping costs (add to total)
   - Verify availability and delivery estimate
   - If total exceeds budget, go back and select another product

8. **Add to Cart**
   - Click "Add to Cart" or "Add to Basket" button
   - Wait for confirmation
   - Proceed to cart/checkout

### Phase 4: Checkout

9. **Review Cart**
   - Verify correct product and quantity
   - Check subtotal and shipping
   - Click "Proceed to Checkout"

10. **Login**
    - Enter the provided email address
    - Click Continue
    - Enter the provided password
    - Click Sign In
    - Handle any "Stay signed in?" prompts

11. **Delivery Address**
    - Select existing default address, OR
    - Select the first available address option
    - Continue to next step

12. **Shipping Options**
    - Select the cheapest shipping option
    - Note the estimated delivery date
    - Continue

13. **Payment Method**
    - Select default payment method if prompted
    - Continue to review

### Phase 5: Order Review

14. **Final Review**
    - Verify product name and quantity
    - Confirm price and shipping
    - Calculate TOTAL cost
    - **CRITICAL**: If total > budget, STOP and report

## Safety Rules

### Hard Stops
- **NEVER** proceed if total exceeds the specified budget
- **STOP** immediately if SMS/email verification is required
- **PAUSE** on any CAPTCHA or security challenge
- **REPORT** if no suitable products are found

### Dry Run Mode
When the message contains "DRY RUN MODE":
1. Complete all steps through order review
2. **DO NOT** click "Place Order" or "Buy Now"
3. **DO NOT** click any final purchase confirmation
4. Report the following:
   - Product name and description
   - Unit price
   - Shipping cost
   - Order total
   - Estimated delivery
   - Whether budget is satisfied

### Live Mode
When NOT in dry run mode:
1. Complete all steps including final purchase
2. Click "Place Order" or equivalent
3. Wait for order confirmation
4. Report order confirmation number
5. Report final charged amount

## Error Handling

### No Products Found
- Try alternative search terms
- Check for typos in search
- Report if no products match criteria

### Out of Stock
- Skip to next product
- Report if all matching products are unavailable

### Login Failed
- Report the error message
- Do not attempt multiple retries (account security)

### Price Changed
- Recalculate total
- Stop if new total exceeds budget
- Report the price change

## Regional Considerations

### Netherlands (amazon.nl)
- Interface in Dutch/English
- Search: "puntenslijper" or "pencil sharpener"
- Prices in EUR

### Germany (amazon.de)
- Interface in German
- Search: "Anspitzer" or "pencil sharpener"
- Prices in EUR

### Other Regions
- Adapt search terms to local language
- Verify currency matches budget constraints

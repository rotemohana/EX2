# Technical Specification & Task Assignment: Dana's Bakery LangGraph System

## 1. Objective
You are an expert AI agent developer. Your task is to generate two things for this project:
1. A file named `prompt.md` containing the exact technical specification (as provided in this prompt).
2. A complete Google Colab Jupyter Notebook (or Python script) implementing a deterministic, Python-based order processing system using **LangGraph** for "Dana's Bakery". 

No LLM calls are permitted; all logic must be executed via pure deterministic Python functions.

---

## 2. Menu and Inventory
The initial inventory and product catalog are defined as follows:
- **challah**: Price = 18₪ | Initial Stock = 10
- **babka**: Price = 45₪ | Initial Stock = 0 (Out of stock)
- **rugelach**: Price = 30₪ | Initial Stock = 3 (Box of rugelach)
- **sourdough**: Price = 25₪ | Initial Stock = 4 (Sourdough loaf)
- **croissants**: Price = 12₪ | **Discontinued** (Must be rejected or treated as invalid).

---

## 3. Business Rules & Logic

### A. Input Validation & Glitches
- If the item is invalid (e.g., "croissants", "pizza", or anything not in the active menu) or if quantity $\le 0$, set `status = "rejected"`, and provide a polite apology message explaining the issue.

### B. Delivery Rules
- **Inside Jerusalem:** Delivery fee is **20₪**. `delivery = "delivery"`.
- **Outside Jerusalem:** We do not deliver outside Jerusalem. Change the order type to **pickup** (`delivery = "pickup"`), fee is **0₪**, and inform the customer politely in the message.

### C. Out-of-Stock & Substitution Chain
- If the requested product has insufficient stock to fulfill the full requested quantity, trigger the substitution fallback chain in this **strict order**:
  1. `babka` $\rightarrow$ suggest `rugelach`
  2. `rugelach` $\rightarrow$ suggest `sourdough`
  3. `sourdough` $\rightarrow$ suggest `challah`
  4. `challah` $\rightarrow$ (no further suggestions)
- **Conditions for substitution:**
  * The substitute product must have *enough stock* for the **entire requested quantity**.
  * The customer receives the exact same quantity of the new product and pays its respective price.
  * Maximum of **2 suggestions** allowed per order. If the second suggestion also fails or cannot be fulfilled, apologize and cancel the order (`status = "rejected"`).

### D. Discount Rules (Avi's Rules)
- **Discount:** **15% off** on the total baked goods price if the order total for baked goods is **strictly greater than 150₪**.
- **Exclusion:** **Never apply discounts on Fridays**, because everything sells out anyway.
- **Scope:** The discount applies **only to baked goods**, never on the delivery fee.

### E. Tone and Persona
- System responses to customers (`message`) must sound warm, personal, and friendly, matching Dana's personal communication style.

---

## 4. Required Graph State Structure
The graph state (`State`) must include:
- `item` (str): The final product item being sold.
- `quantity` (int): The quantity ordered.
- `day` (str): Day of the week (e.g., "Monday", "Friday", "Thursday").
- `city` (str): Customer's city (empty string `""` or `"Jerusalem"`).
- `status` (str): Either `"accepted"` or `"rejected"`.
- `delivery` (str): Either `"pickup"` or `"delivery"`.
- `total` (float/int): Final amount to pay (including delivery fee and discounts).
- `message` (str): Warm reply message to the customer.
- `steps` (list of str): Chronological diary logging all the steps/transitions the order went through.
- `suggestions_count` (int): Counter tracking how many substitution attempts have been made.

---

## 5. Required Output Format
Every execution via `graph.invoke({...})` must return a dictionary containing **exactly** these six keys:
1. `status`
2. `item`
3. `delivery`
4. `total`
5. `message`
6. `steps`

---

## 6. Technical Requirements & Deliverables
1. **`prompt.md`**: Create a file named `prompt.md` containing this exact technical specification text.
2. **LangGraph Notebook/Code**:
   - Built using **LangGraph** in Google Colab.
   - Pure deterministic Python logic (no API keys, no LLM invocations).
   - Include code to draw the graph using `draw_mermaid_png()`.
   - Must include at least **6 diverse test orders** covering all execution paths (successful orders, discounted orders, Friday orders, out-of-stock substitutions, outside-Jerusalem conversions, and rejected/cancelled orders).

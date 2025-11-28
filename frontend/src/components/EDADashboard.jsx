import React, { useState } from 'react';

const EDADashboard = () => {
  const [activeHead, setActiveHead] = useState('Customers');

  const starSchema = [
    { table: "FactSales", type: "Fact", columns: ["sale_id", "customer_id", "medicine_id", "shop_id", "final_price", "status"] },
    { table: "DimCustomer", type: "Dimension", columns: ["customer_id", "full_name", "age", "city", "phone", "email"] },
    { table: "DimMedicine", type: "Dimension", columns: ["medicine_id", "medicine_name", "type_id", "price", "brand"] },
    { table: "DimShop", type: "Dimension", columns: ["shop_id", "location", "manager_name", "rating"] },
    { table: "DimPrescription", type: "Dimension", columns: ["prescription_id", "doctor_name", "dosage", "date"] },
    { table: "FactStock", type: "Fact", columns: ["stock_id", "shop_id", "medicine_id", "available_units"] },
  ];

  const dataHeads = {
    Customers: [
      { customer_id: "CUST1000", full_name: "Ishita Shah", email: "suresh.khan426@gmail.com", city: "Ahmedabad", age: 66 },
      { customer_id: "CUST1001", full_name: "Anita Singh", email: "priya.shah608@gmail.com", city: "Chennai", age: 35 },
      { customer_id: "CUST1002", full_name: "Arjun Khan", email: "ishita.shah208@gmail.com", city: "Hyderabad", age: 32 },
    ],
    Medicine: [
      { medicine_id: "MED2000", medicine_name: "Drug4806", type_id: "TYP112", price: 319.0, brand: "Dr Reddy's" },
      { medicine_id: "MED2001", medicine_name: "Drug13", type_id: "TYP119", price: 407.0, brand: "Dr Reddy's" },
      { medicine_id: "MED2002", medicine_name: "Drug3936", type_id: "TYP105", price: 421.0, brand: "Cipla" },
    ],
    SalesBills: [
      { sale_id: "SALE5000", customer_id: "CUST4690", final_price: 483.0, status: "Cancelled", payment_mode: "Card" },
      { sale_id: "SALE5001", customer_id: "CUST4223", final_price: 565.0, status: "Pending", payment_mode: "UPI" },
      { sale_id: "SALE5002", customer_id: "CUST1800", final_price: 204.0, status: "Cancelled", payment_mode: "Cash" },
    ]
  };

  const steps = [
    {
      title: "1. Entity Relationship Mapping",
      description: "Mapped raw CSVs to a Star Schema. Identified Fact tables (Sales, Stock) and Dimension tables.",
      details: ["Defined relationships: Sales.customer_id -> Customers", "Designed for analytical queries."],
      code: `# Star Schema Design
# Fact Tables: SalesBills, Stocks
# Dimension Tables: Customers, Medicine, PharmacyShops, Prescriptions

# Example Relationship Check
sales_bills['customer_id'].isin(customers['customer_id']).all()`,
      output: "True"
    },
    {
      title: "2. Data Quality & Validity",
      description: "Performed comprehensive checks on dataset integrity.",
      details: ["Checked for missing values.", "Validated numerical ranges (Age, Price)."],
      code: `def check_ranges(df, col, min_val, max_val):
    invalid = df[(df[col] < min_val) | (df[col] > max_val)]
    return invalid.shape[0]

# Check Age Validity
invalid_ages = check_ranges(customers, 'age', 0, 100)
print(f"Invalid Ages: {invalid_ages}")`,
      output: "Invalid Ages: 19"
    },
    {
      title: "2.5 Handling Missing Values",
      description: "Addressed missing data points, specifically in the 'Age' column.",
      details: ["Identified 313 missing age values.", "Imputed missing ages using the Median to avoid skewing the distribution."],
      code: `# Handling missing Age values
median_age = customers['age'].median()
customers['age'].fillna(median_age, inplace=True)

# Verify
print(f"Missing ages after imputation: {customers['age'].isnull().sum()}")`,
      output: "Missing ages after imputation: 0"
    },
    {
      title: "3. Data Cleansing",
      description: "Standardized and cleaned the data.",
      details: ["Standardized city names (e.g., 'Hydrabad' -> 'Hyderabad').", "Validated emails and phones."],
      code: `city_map = {
    'Kolkatta': 'Kolkata',
    'Hydrabad': 'Hyderabad',
    'Mumbai': 'Mumbai'
}
customers['city'] = customers['city'].replace(city_map).str.title()

# Email Validation
customers['valid_email'] = customers['email'].apply(lambda x: bool(re.match(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$', str(x))))`,
      output: "City names standardized. Invalid emails flagged."
    },
    {
      title: "4. Transformation & Feature Engineering",
      description: "Created new features for analysis.",
      details: ["Derived 'expected_amount' = quantity * price.", "Encoded categorical variables."],
      code: `# Feature Creation
sales_bills['expected_amount'] = sales_bills['quantity'] * sales_bills['price']

# One-Hot Encoding
encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
encoded_payment = encoder.fit_transform(sales_bills[['payment_mode']])`,
      output: "New features added: expected_amount, payment_mode_Card, payment_mode_UPI..."
    }
  ];

  return (
    <div className="eda-dashboard" style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', color: '#e2e8f0' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '40px', color: '#38bdf8' }}>Exploratory Data Analysis (EDA) Journey</h2>
      
      {/* Star Schema Section */}
      <div className="glass-panel" style={{ marginBottom: '40px', padding: '20px', border: '1px solid #334155', borderRadius: '10px' }}>
        <h3 style={{ color: '#f472b6', marginBottom: '20px' }}>Target Star Schema</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          {starSchema.map((t, i) => (
            <div key={i} style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', borderLeft: `4px solid ${t.type === 'Fact' ? '#f472b6' : '#38bdf8'}` }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#fff' }}>{t.table} <span style={{ fontSize: '0.8em', opacity: 0.7 }}>({t.type})</span></h4>
              <ul style={{ paddingLeft: '20px', margin: 0, fontSize: '0.9em', color: '#94a3b8' }}>
                {t.columns.map(c => <li key={c}>{c}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Data Heads Section */}
      <div className="glass-panel" style={{ marginBottom: '40px', padding: '20px', border: '1px solid #334155', borderRadius: '10px' }}>
        <h3 style={{ color: '#38bdf8', marginBottom: '20px' }}>Data Previews</h3>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          {Object.keys(dataHeads).map(k => (
            <button 
              key={k} 
              onClick={() => setActiveHead(k)}
              style={{ 
                padding: '8px 16px', 
                borderRadius: '20px', 
                border: '1px solid #38bdf8', 
                background: activeHead === k ? '#38bdf8' : 'transparent',
                color: activeHead === k ? '#000' : '#38bdf8',
                cursor: 'pointer'
              }}
            >
              {k}
            </button>
          ))}
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ background: '#334155' }}>
                {Object.keys(dataHeads[activeHead][0]).map(h => (
                  <th key={h} style={{ padding: '10px', textAlign: 'left', color: '#fff' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataHeads[activeHead].map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                  {Object.values(row).map((v, j) => (
                    <td key={j} style={{ padding: '10px' }}>{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* EDA Steps Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
        {steps.map((step, index) => (
          <div key={index} className="glass-panel" style={{ padding: '25px', borderLeft: '4px solid #38bdf8', background: '#0f172a', borderRadius: '8px' }}>
            <h3 style={{ color: '#38bdf8', margin: '0 0 10px 0' }}>{step.title}</h3>
            <p style={{ color: '#e2e8f0', fontSize: '1.1rem', marginBottom: '15px' }}>{step.description}</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <h4 style={{ color: '#94a3b8', marginBottom: '10px' }}>Details</h4>
                <ul style={{ margin: '0 0 0 20px', color: '#cbd5e1' }}>
                  {step.details.map((detail, i) => (
                    <li key={i} style={{ marginBottom: '5px' }}>{detail}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 style={{ color: '#94a3b8', marginBottom: '10px' }}>Code Snippet</h4>
                <div style={{ background: '#1e293b', padding: '15px', borderRadius: '5px', fontFamily: 'monospace', fontSize: '0.85rem', overflowX: 'auto' }}>
                  <pre style={{ margin: 0, color: '#a5b4fc' }}>{step.code}</pre>
                </div>
                <div style={{ marginTop: '10px', background: '#000', padding: '10px', borderRadius: '5px', borderLeft: '3px solid #22c55e' }}>
                  <span style={{ color: '#22c55e', fontSize: '0.8rem', fontWeight: 'bold' }}>OUTPUT: </span>
                  <span style={{ color: '#fff', fontSize: '0.85rem', fontFamily: 'monospace' }}>{step.output}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EDADashboard;

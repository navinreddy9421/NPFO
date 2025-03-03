frappe.ui.form.on('Employee', {
    refresh(frm) {
        // Function to update salary component filters in custom_earnings and custom_deductions
        function update_salary_components(table_field) {
            frm.fields_dict[table_field].grid.get_field('salary_component').get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        'type': table_field === 'custom_earnings' ? 'Earning' : 'Deduction'
                    }
                };
            };
        }

        update_salary_components('custom_earnings');
        update_salary_components('custom_deductions');
    },

    custom_salary_structure(frm) {
        if (frm.doc.custom_salary_structure) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Salary Structure',
                    name: frm.doc.custom_salary_structure
                },
                callback: function(r) {
                    if (r.message) {
                        let salary_structure = r.message;

                        // Clear existing records in custom_earnings
                        frm.clear_table('custom_earnings');

                        // Populate custom_earnings from Salary Structure's earnings table
                        (salary_structure.earnings || []).forEach(row => {
                            let child = frm.add_child('custom_earnings');

                            // Assign values manually, ensuring all required fields are included
                            child.salary_component = row.salary_component;
                            child.abbr = row.abbr || '';  // Ensure abbr is assigned
                            child.amount = row.amount;
                            child.default_amount = row.default_amount;
                            child.depends_on_lwp = row.depends_on_lwp;
                            child.depends_on_payment_days = row.depends_on_payment_days || 0; // Checkbox field
                            child.statistical_component = row.statistical_component || 0; // Checkbox field
                            child.do_not_include_in_total = row.do_not_include_in_total || 0; // Checkbox field
                            child.deduct_full_tax_on_selected_payroll_date = row.deduct_full_tax_on_selected_payroll_date || 0; // Checkbox field
                            child.condition = row.condition;
                        });

                        // Refresh child table to display correctly
                        frm.refresh_field('custom_earnings');
                    }
                }
            });
        } else {
            frm.clear_table('custom_earnings');
            frm.refresh_field('custom_earnings');
        }
    },

    before_save(frm) {
        // Get all child table values before saving
        let child_data = frm.doc.custom_earnings.map(row => ({ ...row }));
        console.log("Child Table Data on Save:", child_data);
    }
});
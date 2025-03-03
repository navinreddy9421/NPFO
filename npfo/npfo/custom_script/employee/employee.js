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

                        // Clear existing custom_earnings table
                        frm.clear_table('custom_earnings');

                        // Populate custom_earnings from Salary Structure's earnings table
                        (salary_structure.earnings || []).forEach(row => {
                            let child = frm.add_child('custom_earnings');
                            
                            // Copy all fields dynamically
                            Object.assign(child, row);
                        });

                        // Refresh the child table
                        frm.refresh_field('custom_earnings');
                    }
                }
            });
        } else {
            frm.clear_table('custom_earnings');
            frm.refresh_field('custom_earnings');
        }
    }
});

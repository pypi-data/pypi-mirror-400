import React, { useState, useEffect } from 'react';
import { Plus, ArrowRight, X, Save, Database, RefreshCw } from 'lucide-react';
import { api } from './services/api';

const domainOptions = [
  { id: 'CPG', name: 'CPG', description: 'Consumer Packaged Goods', count: 4 },
  { id: 'BFSI', name: 'BFSI', description: 'Banking & Financial Services', count: 10 },
  { id: 'Hospital', name: 'Hospital', description: 'Healthcare Management', count: 1 }
];

const DataTransformationUI = () => {
  const [activeTab, setActiveTab] = useState('tables');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('CPG');
  const [selectedSilverDomain, setSelectedSilverDomain] = useState('CPG');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Hardcoded domain-based bronze tables
  const domainTables = {
    CPG: [
      { 
        name: "purchase_order",
        columns: ["po_num", "po_line", "vendor_code", "vendor_name", "vendor_country", "item_code", "item_desc", "ordered_qty", "received_qty", "rejected_qty", "price", "uom", "po_order_date", "expected_date", "received_date", "po_status", "po_type", "plant_code", "region", "line_status", "change_flag", "storage_location", "inspector", "inspection_status", "accepted_qty", "grn_number", "blocked_flag", "currency", "payment_terms", "created_by"]
      },
      { 
        name: "product_master",
        columns: ["item_code", "item_name", "brand_code", "brand_name", "brand_category", "category_code", "category_name", "material_code", "material_group", "packaging", "size", "variant", "uom", "units_per_case", "cost", "shelf_life", "launch_date", "discontinue_date", "recycling_code", "lifecycle_status", "sustainable_flag", "is_active"]
      },
      { 
        name: "vendor_master",
        columns: ["vendor_code", "vendor_name", "vendor_country", "vendor_category", "region", "sustainable_flag", "sustainability_rating", "compliance_score", "blocked_flag"]
      },
      { 
        name: "material_master",
        columns: ["material_code", "material_name", "material_group", "material_type", "base_uom", "standard_cost", "shelf_life", "hazardous_indicator", "lifecycle_status", "sustainable_flag", "sustainability_cert_code"]
      }
    ],
    BFSI: [
      {
        name: "raw_global_incoterms",
        columns: ["inc_surrogate_key", "incoterm_cd", "incoterm_description", "inc_version", "delivery_grp", "seller_duties", "buyer_duties", "risk_xfer_pt", "cost_xfer_pt", "transport_modes", "insurance_party", "export_clear_party", "import_clear_party", "loading_party", "unload_party", "container_suitable", "bulk_suitable", "doc_requirements", "usage_scenarios", "risk_level", "status_ind", "created_by_user", "creation_date", "source_system_name", "last_updated", "data_quality_score"]
      },
      {
        name: "raw_document_tracking",
        columns: ["doc_track_id", "trade_transaction_id", "doc_type_code", "submission_date", "doc_ref_num", "doc_date_str", "doc_issuer_name", "doc_value_amount", "document_currency", "quantity_shipped", "unit_of_measure", "unit_price", "vessel_name", "voyage_number", "bl_date", "shipment_date", "doc_status_code", "verification_date", "verified_by", "discrepancy_details", "waiver_requested", "waiver_approved", "waiver_approval_date", "original_received", "copies_count", "legalization_status", "endorsement_status", "translation_status", "digital_format_received", "authenticity_verified", "courier_tracking_number", "received_from", "forwarded_to", "retention_start_date", "retention_end_date", "digitization_status", "archive_location", "record_created_by", "record_created_timestamp", "source_system_info"]
      }
    ],
    Hospital: [
      {
        name: "patient_master",
        columns: ["patient_id", "first_name", "last_name", "dob", "gender", "contact_number"]
      }
    ]
  };

  // Get bronze tables for selected domain
  const bronzeTables = domainTables[selectedDomain] || [];
  
  // Calculate domain table counts
  const domainTableCounts = {
    'CPG': domainTables.CPG.length,
    'BFSI': domainTables.BFSI.length,
    'Hospital': domainTables.Hospital.length
  };

  // Hardcoded silver tables data
  const silverTablesData = {
    CPG: [
      {
        name: "dim_material_master",
        columns: [
          "material_id",
          "material_name",
          "material_group",
          "material_type",
          "base_uom",
          "standard_cost",
          "shelf_life",
          "hazardous_indicator",
          "lifecycle_status",
          "sustainable_material_flag",
          "sustainability_cert_id"
        ]
      },
      {
        name: "dim_supplier_master",
        columns: [
          "supplier_id",
          "supplier_name",
          "country",
          "vendor_category",
          "region",
          "sustainable_flag",
          "sustainability_rating",
          "compliance_score",
          "blocked_flag"
        ]
      },
      {
        name: "dim_material_category",
        columns: [
          "category_id",
          "material_id",
          "category_name",
          "category_level",
          "description",
          "material_code"
        ]
      },
      {
        name: "dim_certification_registry",
        columns: [
          "cert_id",
          "certifying_body",
          "issue_date",
          "expiry_date",
          "material_id",
          "scope",
          "score"
        ]
      },
      {
        name: "dim_supplier_evaluation",
        columns: [
          "evaluation_id",
          "supplier_id",
          "evaluation_date",
          "performance_rating",
          "evaluation_remarks"
        ]
      },
      {
        name: "fact_purchase_order_header",
        columns: [
          "po_id",
          "supplier_id",
          "po_type",
          "po_status",
          "order_date",
          "currency",
          "created_by",
          "planned_delivery_date",
          "payment_terms"
        ]
      },
      {
        name: "fact_purchase_order_line",
        columns: [
          "po_id",
          "line_item_no",
          "material_id",
          "ordered_qty",
          "price_per_unit",
          "unit_of_measure",
          "expected_delivery_date",
          "plant_id",
          "line_status",
          "change_flag"
        ]
      },
      {
        name: "fact_goods_receipt",
        columns: [
          "grn_id",
          "po_id",
          "line_item_no",
          "material_id",
          "received_qty",
          "receipt_date",
          "storage_location_id",
          "gr_status",
          "inspector_id",
          "inspection_status",
          "accepted_qty",
          "rejected_qty"
        ]
      },
      {
        name: "fact_vendor_performance",
        columns: [
          "supplier_id",
          "month",
          "delivery_accuracy_score",
          "quality_score",
          "contract_compliance_score",
          "review_comments",
          "rating_source"
        ]
      },
      {
        name: "fact_material_inventory",
        columns: [
          "inventory_id",
          "material_id",
          "warehouse_id",
          "snapshot_date",
          "on_hand_qty",
          "reserved_qty"
        ]
      },
      {
        name: "fact_material_price_history",
        columns: [
          "material_id",
          "price_change_date",
          "old_price",
          "new_price",
          "currency",
          "effective_from"
        ]
      },
      {
        name: "dim_product_master",
        columns: [
          "product_id",
          "sku_id",
          "product_name",
          "brand",
          "category",
          "size",
          "packaging",
          "launch_date",
          "unit_cost",
          "recycling_code",
          "shelf_life",
          "is_active",
          "created_date",
          "updated_date"
        ]
      },
      {
        name: "dim_brand",
        columns: [
          "brand_id",
          "brand_name",
          "brand_code",
          "parent_brand_id",
          "brand_category",
          "manufacturer",
          "is_active",
          "launch_date",
          "discontinue_date",
          "remarks"
        ]
      },
      {
        name: "dim_product_hierarchy",
        columns: [
          "product_id",
          "parent_product_id",
          "hierarchy_level",
          "group_name",
          "category_id",
          "brand_id"
        ]
      },
      {
        name: "fact_manufacturing_order",
        columns: [
          "order_id",
          "order_code",
          "product_id",
          "plant_id",
          "planned_start_date",
          "planned_end_date",
          "actual_start_date",
          "actual_end_date",
          "material_requirements",
          "material_reservation_status",
          "order_status",
          "created_by",
          "created_date",
          "updated_date"
        ]
      },
      {
        name: "fact_production_batch",
        columns: [
          "batch_id",
          "order_id",
          "start_time",
          "end_time",
          "produced_qty",
          "good_qty",
          "scrap_qty",
          "waste_qty",
          "raw_material_used_qty",
          "operator_id",
          "supervisor_id",
          "qc_status",
          "created_date",
          "updated_date"
        ]
      },
      {
        name: "fact_material_consumption",
        columns: [
          "batch_id",
          "material_id",
          "qty_used",
          "unit_of_measure",
          "created_date",
          "updated_date"
        ]
      },
      {
        name: "dim_carrier_master",
        columns: [
          "carrier_id",
          "carrier_name",
          "carrier_mode",
          "transit_lead_time",
          "region",
          "contact_info"
        ]
      },
      {
        name: "fact_shipment_line",
        columns: [
          "shipment_id",
          "product_id",
          "quantity",
          "shipment_type",
          "handling_instructions"
        ]
      },
      {
        name: "dim_warehouse_master",
        columns: [
          "warehouse_id",
          "warehouse_name",
          "warehouse_type",
          "location",
          "capacity_units",
          "facility_id"
        ]
      },
      {
        name: "fact_quality_incident",
        columns: [
          "incident_id",
          "batch_id",
          "product_id",
          "incident_date",
          "incident_type",
          "severity_level",
          "resolution_status",
          "root_cause_code",
          "corrective_action",
          "created_date",
          "updated_date"
        ]
      },
      {
        name: "fact_inventory_adjustment",
        columns: [
          "adjustment_id",
          "product_id",
          "warehouse_id",
          "adjustment_date",
          "adjustment_reason",
          "adjusted_qty",
          "adjustment_type"
        ]
      },
      {
        name: "dim_channel",
        columns: [
          "channel_id",
          "channel_name",
          "parent_channel_id",
          "channel_type"
        ]
      },
      {
        name: "fact_inbound_shipment",
        columns: [
          "shipment_id",
          "source_id",
          "destination_warehouse_id",
          "expected_delivery_date",
          "actual_delivery_date",
          "carrier_id",
          "shipment_status"
        ]
      },
      {
        name: "dim_export_type",
        columns: [
          "export_type_id",
          "export_type_name"
        ]
      },
      {
        name: "fact_outbound_shipment",
        columns: [
          "shipment_id",
          "origin_warehouse_id",
          "destination_id",
          "ship_date",
          "carrier_id",
          "total_weight",
          "shipment_status"
        ]
      }

    ],
    BFSI: [],
    Hospital: []
  };

  // Get silver tables for selected domain
  const silverTables = silverTablesData[selectedSilverDomain] || [];
  
  // Calculate silver domain table counts
  const silverDomainTableCounts = {
    'CPG': silverTablesData.CPG.length,
    'BFSI': silverTablesData.BFSI.length,
    'Hospital': silverTablesData.Hospital.length
  };

  const [pipelines, setPipelines] = useState([]);

  const [newPipeline, setNewPipeline] = useState({
    name: '',
    domain: 'CPG',
    source_table: '',
    target_table: '',
    transformations: []
  });

  const transformationTypes = [
    { value: 'rename_columns', label: 'Rename Columns' },
    { value: 'join', label: 'Join Tables' },
    { value: 'select', label: 'Select Columns' },
    { value: 'derived_column', label: 'Derived Column' }
  ];

  // Load pipelines from backend on component mount
  useEffect(() => {
    loadPipelines();
  }, []);

  const loadPipelines = async (domain = null) => {
    try {
      setLoading(true);
      const data = await api.getPipelines(domain);
      setPipelines(data);
      setError(null);
    } catch (err) {
      console.error('Error loading pipelines:', err);
      setError('Failed to load pipelines from backend');
    } finally {
      setLoading(false);
    }
  };

  const addTransformation = () => {
    setNewPipeline({
      ...newPipeline,
      transformations: [...newPipeline.transformations, {
        type: 'rename_columns',
        mappings: [{ from: '', to: '' }]
      }]
    });
  };

  const updateTransformation = (transformIndex, field, value) => {
    const updated = [...newPipeline.transformations];
    updated[transformIndex] = { ...updated[transformIndex], [field]: value };
    setNewPipeline({ ...newPipeline, transformations: updated });
  };

  const addMapping = (transformIndex) => {
    const updated = [...newPipeline.transformations];
    if (!updated[transformIndex].mappings) updated[transformIndex].mappings = [];
    updated[transformIndex].mappings.push({ from: '', to: '' });
    setNewPipeline({ ...newPipeline, transformations: updated });
  };

  const updateMapping = (transformIndex, mappingIndex, field, value) => {
    const updated = [...newPipeline.transformations];
    updated[transformIndex].mappings[mappingIndex][field] = value;
    setNewPipeline({ ...newPipeline, transformations: updated });
  };

  const removeMapping = (transformIndex, mappingIndex) => {
    const updated = [...newPipeline.transformations];
    updated[transformIndex].mappings.splice(mappingIndex, 1);
    setNewPipeline({ ...newPipeline, transformations: updated });
  };

  const removeTransformation = (transformIndex) => {
    const updated = newPipeline.transformations.filter((_, i) => i !== transformIndex);
    setNewPipeline({ ...newPipeline, transformations: updated });
  };

  const getAvailableColumns = (tableName) => {
    const table = domainTables[newPipeline.domain].find(t => t.name === tableName);
    return table ? table.columns : [];
  };

  const createPipeline = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate required fields
      if (!newPipeline.name || !newPipeline.source_table || !newPipeline.target_table) {
        alert('Please fill in all required fields: Pipeline Name, Source Table, and Target Table');
        setLoading(false);
        return;
      }

      // Transform the data to match backend schema
      const pipelineData = {
        name: newPipeline.name,
        domain: newPipeline.domain,
        source_table: newPipeline.source_table,
        target_table: newPipeline.target_table,
        transformations: newPipeline.transformations.map(t => ({
          type: t.type,
          mappings: t.mappings?.map(m => ({
            from_col: m.from,
            to: m.to
          })),
          condition: t.condition,
          selected_columns: t.selected_columns,
          new_column_name: t.new_column_name,
          expression: t.expression
        }))
      };

      // Create pipeline via API
      await api.createPipeline(pipelineData);
      
      // Reload pipelines from backend
      await loadPipelines(newPipeline.domain);
      
      // Close modal and reset form
      setShowCreateModal(false);
      setNewPipeline({
        name: '',
        domain: 'CPG',
        source_table: '',
        target_table: '',
        transformations: []
      });
      
      alert('Pipeline created successfully!');
    } catch (err) {
      console.error('Error creating pipeline:', err);
      setError('Failed to create pipeline: ' + err.message);
      alert('Failed to create pipeline: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRunPipeline = async (pipelineId, pipelineName) => {
    if (!window.confirm(`Are you sure you want to run pipeline: ${pipelineName}?\n\nThis will execute the transformations in Snowflake.`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await api.executePipeline(pipelineId);
      
      alert(`✅ Pipeline executed successfully!\n\n${result.message}\nRows processed: ${result.rows_processed}`);
      
      // Reload pipelines to refresh status
      await loadPipelines();
    } catch (err) {
      console.error('Error executing pipeline:', err);
      setError('Failed to execute pipeline: ' + err.message);
      alert('❌ Failed to execute pipeline:\n\n' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePipeline = async (pipelineId, pipelineName) => {
    if (!window.confirm(`Are you sure you want to delete pipeline: ${pipelineName}?\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await api.deletePipeline(pipelineId);
      
      alert('Pipeline deleted successfully!');
      
      // Reload pipelines
      await loadPipelines();
    } catch (err) {
      console.error('Error deleting pipeline:', err);
      setError('Failed to delete pipeline: ' + err.message);
      alert('Failed to delete pipeline: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportConfig = async () => {
    try {
      setLoading(true);
      const config = await api.exportConfig();
      
      // Download as JSON file
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pipeline_config.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      alert('Config exported successfully!');
    } catch (err) {
      console.error('Error exporting config:', err);
      alert('Failed to export config: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="mx-auto">
        {/* Enhanced Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">Data Mapper Pipeline</h1>
          </div>
          <div className="flex items-center gap-3">
            {/* Backend Connection Status */}
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              error ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
            }`}>
              {error ? '⚠️ Backend Error' : '✅ Connected'}
            </div>
            {/* Export Config Button */}
            <button
              onClick={handleExportConfig}
              disabled={loading}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors duration-200 flex items-center gap-2 text-sm disabled:bg-gray-400"
            >
              <Save className="w-4 h-4" />
              Export Config
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
            <span className="text-red-600">⚠️</span>
            <span className="text-red-800 text-sm">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Enhanced Tabs */}
        <div className="mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-1 w-fit">
            <nav className="flex space-x-1">
              <button
                onClick={() => setActiveTab('tables')}
                className={`px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
                  activeTab === 'tables' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                Raw data
              </button>
              <button
                onClick={() => setActiveTab('silver')}
                className={`px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
                  activeTab === 'silver' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                Canonical data model
              </button>
              <button
                onClick={() => setActiveTab('pipelines')}
                className={`px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
                  activeTab === 'pipelines' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                Pipelines ({pipelines.length})
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'tables' && (
          <div>
            {/* Domain Selection */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Select Domain</h3>
                    <p className="text-gray-500 text-sm">Choose a domain to explore bronze tables</p>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl">
                {[
                  { 
                    key: 'CPG', 
                    label: 'CPG', 
                    icon: '🛍️', 
                    title: 'Consumer Packaged Goods',
                    desc: 'Retail and consumer products data',
                    color: 'from-pink-500 to-rose-500',
                    bgColor: 'bg-pink-50',
                    borderColor: 'border-pink-200',
                    textColor: 'text-pink-700'
                  },
                  { 
                    key: 'BFSI', 
                    label: 'BFSI', 
                    icon: '🏦', 
                    title: 'Banking & Financial Services',
                    desc: 'Financial transactions and banking data',
                    color: 'from-blue-500 to-indigo-500',
                    bgColor: 'bg-blue-50',
                    borderColor: 'border-blue-200',
                    textColor: 'text-blue-700'
                  },
                  { 
                    key: 'Hospital', 
                    label: 'Hospital', 
                    icon: '🏥', 
                    title: 'Healthcare Management',
                    desc: 'Medical and healthcare data systems',
                    color: 'from-green-500 to-emerald-500',
                    bgColor: 'bg-green-50',
                    borderColor: 'border-green-200',
                    textColor: 'text-green-700'
                  }
                ].map((domain) => (
                  <button
                    key={domain.key}
                    onClick={() => setSelectedDomain(domain.key)}
                    className={`group relative p-6 rounded-2xl border-2 transition-all duration-300 text-left transform hover:scale-105 hover:-translate-y-1 ${
                      selectedDomain === domain.key
                        ? `bg-gradient-to-br ${domain.color} text-white border-transparent shadow-2xl`
                        : `bg-white ${domain.bgColor} ${domain.borderColor} hover:shadow-xl hover:shadow-gray-200`
                    }`}
                  >
                    {selectedDomain === domain.key && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-lg">
                        <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${
                        selectedDomain === domain.key 
                          ? 'bg-white bg-opacity-20' 
                          : domain.bgColor
                      }`}>
                        {domain.icon}
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        selectedDomain === domain.key
                          ? 'bg-white bg-opacity-20 text-white'
                          : `${domain.textColor} ${domain.bgColor}`
                      }`}>
                        {domainTableCounts[domain.key]} tables
                      </div>
                    </div>
                    
                    <div>
                      <h4 className={`font-bold text-lg mb-2 ${
                        selectedDomain === domain.key ? 'text-white' : 'text-gray-900'
                      }`}>
                        {domain.label}
                      </h4>
                      <p className={`text-sm font-medium mb-2 ${
                        selectedDomain === domain.key ? 'text-white text-opacity-90' : 'text-gray-600'
                      }`}>
                        {domain.title}
                      </p>
                      <p className={`text-xs ${
                        selectedDomain === domain.key ? 'text-white text-opacity-70' : 'text-gray-500'
                      }`}>
                        {domain.desc}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Tables Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {bronzeTables.map((table) => (
                <div key={table.name} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 p-4 border border-gray-100">
                  <h3 className="font-medium text-gray-900 mb-3">{table.name}</h3>
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600 mb-2">
                      Columns ({table.columns.length}):
                    </p>
                    <div className="max-h-32 overflow-y-auto">
                      {table.columns.map((column) => (
                        <span key={column} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs mr-2 mb-1">
                          {column}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'silver' && (
          <div>
            {/* Domain Selection for Silver */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Select Domain</h3>
                    <p className="text-gray-500 text-sm">Choose a domain to view silver transformations</p>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl">
                {[
                  { 
                    key: 'CPG', 
                    label: 'CPG', 
                    icon: '🛍️', 
                    title: 'Consumer Packaged Goods',
                    desc: 'Refined retail and consumer data',
                    color: 'from-pink-500 to-rose-500',
                    bgColor: 'bg-pink-50',
                    borderColor: 'border-pink-200',
                    textColor: 'text-pink-700'
                  }
                ].map((domain) => (
                  <button
                    key={domain.key}
                    onClick={() => setSelectedSilverDomain(domain.key)}
                    className={`group relative p-6 rounded-2xl border-2 transition-all duration-300 text-left transform hover:scale-105 hover:-translate-y-1 ${
                      selectedSilverDomain === domain.key
                        ? `bg-gradient-to-br ${domain.color} text-white border-transparent shadow-2xl`
                        : `bg-white ${domain.bgColor} ${domain.borderColor} hover:shadow-xl hover:shadow-gray-200`
                    }`}
                  >
                    {selectedSilverDomain === domain.key && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-lg">
                        <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${
                        selectedSilverDomain === domain.key 
                          ? 'bg-white bg-opacity-20' 
                          : domain.bgColor
                      }`}>
                        {domain.icon}
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        selectedSilverDomain === domain.key
                          ? 'bg-white bg-opacity-20 text-white'
                          : `${domain.textColor} ${domain.bgColor}`
                      }`}>
                        {silverDomainTableCounts[domain.key]} tables
                      </div>
                    </div>
                    
                    <div>
                      <h4 className={`font-bold text-lg mb-2 ${
                        selectedSilverDomain === domain.key ? 'text-white' : 'text-gray-900'
                      }`}>
                        {domain.label}
                      </h4>
                      <p className={`text-sm font-medium mb-2 ${
                        selectedSilverDomain === domain.key ? 'text-white text-opacity-90' : 'text-gray-600'
                      }`}>
                        {domain.title}
                      </p>
                      <p className={`text-xs ${
                        selectedSilverDomain === domain.key ? 'text-white text-opacity-70' : 'text-gray-500'
                      }`}>
                        {domain.desc}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Silver Tables Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {silverTables.map((table, index) => (
                <div key={index} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 p-4 border border-gray-100">
                  <h3 className="font-medium text-gray-900 mb-3">{table.name}</h3>
                  {table.description && <p className="text-sm text-gray-600 mb-3">{table.description}</p>}
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600 mb-2">
                      Columns ({table.columns.length}):
                    </p>
                    <div className="max-h-32 overflow-y-auto">
                      {table.columns.map((column) => (
                        <span key={column} className="inline-block bg-green-100 text-green-700 px-2 py-1 rounded text-xs mr-2 mb-1">
                          {column}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'pipelines' && (
          <div className="space-y-6">
            {/* Create Pipeline Button */}
            <div className="flex justify-between items-center">
              <button 
                onClick={() => setShowCreateModal(true)}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2 shadow-lg text-sm disabled:bg-gray-400"
              >
                <Plus className="w-4 h-4" />
                Create Pipeline
              </button>
              
              {loading && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Loading...</span>
                </div>
              )}
            </div>

            {/* Pipelines Content */}
            {pipelines.length > 0 ? (
              <div className="space-y-4">
                {pipelines.map((pipeline) => (
                  <div key={pipeline.id} className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-gray-900 text-lg">{pipeline.name}</h3>
                      <button
                        onClick={() => handleDeletePipeline(pipeline.id, pipeline.name)}
                        className="text-red-600 hover:text-red-800 p-2 rounded-lg hover:bg-red-50"
                        title="Delete Pipeline"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                        {pipeline.domain}
                      </span>
                      <span>{pipeline.source_table}</span>
                      <ArrowRight className="w-4 h-4" />
                      <span>{pipeline.target_table}</span>
                      {pipeline.status && (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          pipeline.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {pipeline.status}
                        </span>
                      )}
                    </div>
                    
                    <div className="space-y-2">
                      {pipeline.transformations.map((transform, tIndex) => (
                        <div key={tIndex} className="bg-gray-50 p-3 rounded">
                          <p className="font-medium text-sm capitalize">{transform.type.replace('_', ' ')}</p>
                          {transform.mappings && (
                            <div className="mt-2 space-y-1">
                              {transform.mappings.map((mapping, mIndex) => (
                                <div key={mIndex} className="text-sm text-gray-600">
                                  <span className="font-mono bg-gray-200 px-1 rounded">{mapping.from_col || mapping.from}</span>
                                  <ArrowRight className="w-3 h-3 inline mx-2" />
                                  <span className="font-mono bg-green-200 px-1 rounded">{mapping.to}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {transform.condition && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Join Condition:</p>
                              <div className="text-sm text-gray-600 font-mono bg-blue-50 p-2 rounded">
                                {transform.condition}
                              </div>
                            </div>
                          )}
                          {transform.selected_columns && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Selected Columns:</p>
                              <div className="flex flex-wrap gap-1">
                                {transform.selected_columns.map((col) => (
                                  <span key={col} className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">
                                    {col}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {transform.expression && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Expression:</p>
                              <div className="text-sm text-gray-600 font-mono bg-yellow-50 p-2 rounded">
                                {transform.new_column_name} = {transform.expression}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    {/* Pipeline Actions */}
                    <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2">
                      <button 
                        onClick={() => handleRunPipeline(pipeline.id, pipeline.name)}
                        disabled={loading}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors duration-200 flex items-center gap-2 text-sm font-medium disabled:bg-gray-400"
                      >
                        <RefreshCw className="w-4 h-4" />
                        Run Pipeline
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Database className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No pipelines found</h3>
                <p className="text-gray-500 mb-6">Create your first data transformation pipeline to get started</p>
              </div>
            )}
          </div>
        )}

        {/* Create Pipeline Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[95vh] flex flex-col border border-gray-200">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 text-white rounded-t-2xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                      <Plus className="w-6 h-6" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">Create New Pipeline</h2>
                      <p className="text-blue-100 text-sm">Define data transformation rules and mappings</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setShowCreateModal(false)}
                    className="w-8 h-8 bg-white bg-opacity-20 rounded-lg flex items-center justify-center hover:bg-opacity-30 transition-all duration-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="flex-1 p-6 space-y-6 overflow-y-auto">
                {/* Basic Info Section */}
                <div className="bg-gray-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    Pipeline Information
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Pipeline Name *</label>
                      <input
                        type="text"
                        value={newPipeline.name}
                        onChange={(e) => setNewPipeline({...newPipeline, name: e.target.value})}
                        placeholder="Enter a descriptive name for your pipeline"
                        className="w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Domain *</label>
                      <select
                        value={newPipeline.domain}
                        onChange={(e) => setNewPipeline({
                          ...newPipeline, 
                          domain: e.target.value,
                          source_table: '',
                          target_table: ''
                        })}
                        className="w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                      >
                        <option value="CPG">🛍️ CPG - Consumer Packaged Goods</option>
                        <option value="BFSI">🏦 BFSI - Banking & Financial Services</option>
                        <option value="Hospital">🏥 Hospital - Healthcare Management</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Source Table *</label>
                        <select
                          value={newPipeline.source_table}
                          onChange={(e) => setNewPipeline({...newPipeline, source_table: e.target.value})}
                          className="w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                        >
                          <option value="">Select source table from {newPipeline.domain} domain</option>
                          {domainTables[newPipeline.domain].map((table) => (
                            <option key={table.name} value={table.name}>{table.name}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Target Table *</label>
                        <select
                          value={newPipeline.target_table}
                          onChange={(e) => setNewPipeline({...newPipeline, target_table: e.target.value})}
                          className="w-full border-2 border-gray-200 rounded-lg px-4 py-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                        >
                          <option value="">Select target table for {newPipeline.domain} domain</option>
                          {silverTablesData[newPipeline.domain].map((table) => (
                            <option key={table.name} value={table.name}>{table.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Transformations Section */}
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                        <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </div>
                      Data Transformations
                    </h3>
                    <button
                      onClick={addTransformation}
                      className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 shadow-md"
                    >
                      <Plus className="w-4 h-4" />
                      Add Transformation
                    </button>
                  </div>

                  {newPipeline.transformations.map((transformation, tIndex) => (
                    <div key={tIndex} className="bg-white border-2 border-gray-200 rounded-xl p-4 mb-4 shadow-sm hover:shadow-md transition-all duration-200">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span className="text-blue-600 font-semibold text-sm">{tIndex + 1}</span>
                          </div>
                          <select
                            value={transformation.type}
                            onChange={(e) => updateTransformation(tIndex, 'type', e.target.value)}
                            className="border-2 border-gray-200 rounded-lg px-3 py-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 font-medium"
                          >
                            {transformationTypes.map((type) => (
                              <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                          </select>
                        </div>
                        <button
                          onClick={() => removeTransformation(tIndex)}
                          className="w-8 h-8 bg-red-100 text-red-600 rounded-lg flex items-center justify-center hover:bg-red-200 transition-all duration-200"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Rename Columns */}
                      {transformation.type === 'rename_columns' && (
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-4">
                            <span className="text-sm font-semibold text-gray-700 flex items-center">
                              <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                              </svg>
                              Column Mappings
                            </span>
                            <button
                              onClick={() => addMapping(tIndex)}
                              className="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 hover:bg-green-700 transition-all duration-200"
                            >
                              <Plus className="w-3 h-3" />
                              Add Mapping
                            </button>
                          </div>
                          <div className="space-y-3">
                            {transformation.mappings?.map((mapping, mIndex) => (
                              <div key={mIndex} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200">
                                <select
                                  value={mapping.from}
                                  onChange={(e) => updateMapping(tIndex, mIndex, 'from', e.target.value)}
                                  className="flex-1 border-2 border-gray-200 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                                >
                                  <option value="">Select source column</option>
                                  {getAvailableColumns(newPipeline.source_table).map((col) => (
                                    <option key={col} value={col}>{col}</option>
                                  ))}
                                </select>
                                <div className="flex items-center justify-center w-8 h-8 bg-gray-100 rounded-lg">
                                  <ArrowRight className="w-4 h-4 text-gray-500" />
                                </div>
                                <select
                                  value={mapping.to}
                                  onChange={(e) => updateMapping(tIndex, mIndex, 'to', e.target.value)}
                                  className="flex-1 border-2 border-gray-200 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                                >
                                  <option value="">Select target column</option>
                                  {newPipeline.target_table && silverTablesData[newPipeline.domain].find(table => table.name === newPipeline.target_table)?.columns.map((col) => (
                                    <option key={col} value={col}>{col}</option>
                                  ))}
                                </select>
                                <button
                                  onClick={() => removeMapping(tIndex, mIndex)}
                                  className="w-8 h-8 bg-red-100 text-red-600 rounded-lg flex items-center justify-center hover:bg-red-200 transition-all duration-200"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Join Tables */}
                      {transformation.type === 'join' && (
                        <div className="bg-gray-50 rounded-lg p-4">
                          <label className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                            Join Condition
                          </label>
                          <input
                            type="text"
                            placeholder="e.g., table1.id = table2.id"
                            value={transformation.condition || ''}
                            onChange={(e) => updateTransformation(tIndex, 'condition', e.target.value)}
                            className="w-full border-2 border-gray-200 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                          />
                        </div>
                      )}

                      {/* Select Columns */}
                      {transformation.type === 'select' && (
                        <div className="bg-gray-50 rounded-lg p-4">
                          <label className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Select Columns
                          </label>
                          <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                            {getAvailableColumns(newPipeline.source_table).map((col) => (
                              <label key={col} className="flex items-center text-sm p-2 bg-white rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200">
                                <input
                                  type="checkbox"
                                  className="mr-2 text-blue-600 focus:ring-blue-500"
                                  onChange={(e) => {
                                    const selected = transformation.selected_columns || [];
                                    if (e.target.checked) {
                                      updateTransformation(tIndex, 'selected_columns', [...selected, col]);
                                    } else {
                                      updateTransformation(tIndex, 'selected_columns', selected.filter((c) => c !== col));
                                    }
                                  }}
                                />
                                <span className="font-mono text-xs">{col}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Derived Column */}
                      {transformation.type === 'derived_column' && (
                        <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                          <div>
                            <label className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                              <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                              </svg>
                              New Column Name
                            </label>
                            <input
                              type="text"
                              placeholder="Enter column name"
                              value={transformation.new_column_name || ''}
                              onChange={(e) => updateTransformation(tIndex, 'new_column_name', e.target.value)}
                              className="w-full border-2 border-gray-200 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                            />
                          </div>
                          <div>
                            <label className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                              <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                              </svg>
                              Expression
                            </label>
                            <input
                              type="text"
                              placeholder="e.g., col1 + col2"
                              value={transformation.expression || ''}
                              onChange={(e) => updateTransformation(tIndex, 'expression', e.target.value)}
                              className="w-full border-2 border-gray-200 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer */}
              <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-3 text-gray-700 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={createPipeline}
                  disabled={loading}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 flex items-center gap-2 font-medium shadow-lg hover:shadow-xl transition-all duration-200 disabled:from-gray-400 disabled:to-gray-400"
                >
                  <Save className="w-4 h-4" />
                  {loading ? 'Creating...' : 'Create Pipeline'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataTransformationUI;

/**
 * Patent Database Backend Service
 * Comprehensive API for Cortellis and Google Patents data
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3005;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Data paths
const DATA_PATHS = {
    cortellis: {
        patents: './processed_data/patents_processed.json',
        drugs: './processed_data/drugs_processed.json',
        relationships: './processed_data/relationships.json',
        patentStats: './processed_data/patent_statistics.json',
        drugStats: './processed_data/drug_statistics.json'
    },
    unified: {
        patents: './unified_patent_data/unified_patents.json',
        drugs: './unified_patent_data/unified_drugs.json',
        masterIndex: './unified_patent_data/master_index.json'
    }
};

// Cache management
class DataCache {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    get(key) {
        const item = this.cache.get(key);
        if (item && Date.now() < item.expiry) {
            return item.data;
        }
        this.cache.delete(key);
        return null;
    }

    set(key, data) {
        this.cache.set(key, {
            data,
            expiry: Date.now() + this.cacheTimeout
        });
    }

    clear() {
        this.cache.clear();
    }
}

const cache = new DataCache();

// Data loading functions
async function loadJsonFile(filePath) {
    try {
        const data = await fs.readFile(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`Error loading ${filePath}:`, error.message);
        return null;
    }
}

async function loadAllData() {
    const cacheKey = 'all_data';
    const cached = cache.get(cacheKey);
    if (cached) return cached;

    const data = {
        patents: [],
        drugs: [],
        relationships: [],
        statistics: {}
    };

    // Try to load unified data first
    const unifiedPatents = await loadJsonFile(DATA_PATHS.unified.patents);
    const unifiedDrugs = await loadJsonFile(DATA_PATHS.unified.drugs);

    if (unifiedPatents && unifiedDrugs) {
        data.patents = unifiedPatents;
        data.drugs = unifiedDrugs;
        data.source = 'unified';
    } else {
        // Fall back to Cortellis data
        const cortellisPatents = await loadJsonFile(DATA_PATHS.cortellis.patents);
        const cortellisDrugs = await loadJsonFile(DATA_PATHS.cortellis.drugs);

        if (cortellisPatents && cortellisDrugs) {
            data.patents = cortellisPatents;
            data.drugs = cortellisDrugs;
            data.source = 'cortellis';
        }
    }

    // Load relationships and statistics
    data.relationships = await loadJsonFile(DATA_PATHS.cortellis.relationships) || [];
    data.statistics = {
        patents: await loadJsonFile(DATA_PATHS.cortellis.patentStats) || {},
        drugs: await loadJsonFile(DATA_PATHS.cortellis.drugStats) || {}
    };

    cache.set(cacheKey, data);
    return data;
}

// Search utilities
function searchPatents(patents, query, filters = {}) {
    let results = patents;

    // Text search
    if (query) {
        const searchTerm = query.toLowerCase();
        results = results.filter(patent => {
            const searchableText = [
                patent.title,
                patent.abstract,
                patent.compound_name,
                ...(patent.drugs || []),
                ...(patent.inventors || []),
                ...(patent.grantees || []),
                patent.patent_number,
                patent.application_number
            ].filter(Boolean).join(' ').toLowerCase();

            return searchableText.includes(searchTerm);
        });
    }

    // Apply filters
    if (filters.classification) {
        results = results.filter(patent =>
            patent.classifications?.some(c =>
                c.toLowerCase().includes(filters.classification.toLowerCase())
            )
        );
    }

    if (filters.drug) {
        results = results.filter(patent =>
            patent.drugs?.some(d =>
                d.toLowerCase().includes(filters.drug.toLowerCase())
            )
        );
    }

    if (filters.company) {
        results = results.filter(patent =>
            patent.grantees?.some(g =>
                g.toLowerCase().includes(filters.company.toLowerCase())
            ) ||
            patent.original_applicants?.some(a =>
                a.toLowerCase().includes(filters.company.toLowerCase())
            )
        );
    }

    if (filters.dateFrom) {
        results = results.filter(patent =>
            patent.application_date >= filters.dateFrom
        );
    }

    if (filters.dateTo) {
        results = results.filter(patent =>
            patent.application_date <= filters.dateTo
        );
    }

    if (filters.hasExpired !== undefined) {
        const now = new Date().toISOString().split('T')[0];
        results = results.filter(patent => {
            const isExpired = patent.earliest_expiry_date && patent.earliest_expiry_date < now;
            return filters.hasExpired ? isExpired : !isExpired;
        });
    }

    return results;
}

function searchDrugs(drugs, query, filters = {}) {
    let results = drugs;

    // Text search
    if (query) {
        const searchTerm = query.toLowerCase();
        results = results.filter(drug => {
            const searchableText = [
                drug.name,
                ...(drug.synonyms || []),
                ...(drug.active_indications || []),
                ...(drug.mechanism_of_action || []),
                ...(drug.targets || []),
                drug.summary
            ].filter(Boolean).join(' ').toLowerCase();

            return searchableText.includes(searchTerm);
        });
    }

    // Apply filters
    if (filters.phase) {
        results = results.filter(drug =>
            drug.highest_phase === filters.phase
        );
    }

    if (filters.indication) {
        results = results.filter(drug =>
            drug.active_indications?.some(i =>
                i.toLowerCase().includes(filters.indication.toLowerCase())
            )
        );
    }

    if (filters.company) {
        results = results.filter(drug =>
            drug.active_companies?.some(c =>
                c.toLowerCase().includes(filters.company.toLowerCase())
            )
        );
    }

    if (filters.target) {
        results = results.filter(drug =>
            drug.targets?.some(t =>
                t.toLowerCase().includes(filters.target.toLowerCase())
            )
        );
    }

    if (filters.launched !== undefined) {
        results = results.filter(drug =>
            filters.launched ? drug.first_launched_date : !drug.first_launched_date
        );
    }

    return results;
}

// API Routes

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        name: 'Patent Database API',
        version: '2.0',
        endpoints: {
            health: '/health',
            statistics: '/api/statistics',
            patents: {
                search: '/api/patents/search',
                detail: '/api/patents/:id',
                byDrug: '/api/patents/drug/:drugName',
                byCompany: '/api/patents/company/:company',
                expired: '/api/patents/expired',
                recent: '/api/patents/recent'
            },
            drugs: {
                search: '/api/drugs/search',
                detail: '/api/drugs/:id',
                byIndication: '/api/drugs/indication/:indication',
                byCompany: '/api/drugs/company/:company',
                byPhase: '/api/drugs/phase/:phase',
                launched: '/api/drugs/launched'
            },
            relationships: '/api/relationships/:type',
            analysis: {
                patentLandscape: '/api/analysis/patent-landscape',
                drugPipeline: '/api/analysis/drug-pipeline',
                competitiveAnalysis: '/api/analysis/competitive/:company',
                expiryTimeline: '/api/analysis/expiry-timeline'
            }
        }
    });
});

// Health check
app.get('/health', async (req, res) => {
    const data = await loadAllData();
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        dataSource: data.source || 'none',
        counts: {
            patents: data.patents.length,
            drugs: data.drugs.length,
            relationships: data.relationships.length
        }
    });
});

// Statistics endpoint
app.get('/api/statistics', async (req, res) => {
    try {
        const data = await loadAllData();
        res.json({
            source: data.source,
            patents: data.statistics.patents,
            drugs: data.statistics.drugs,
            summary: {
                totalPatents: data.patents.length,
                totalDrugs: data.drugs.length,
                totalRelationships: data.relationships.length
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Patent search
app.get('/api/patents/search', async (req, res) => {
    try {
        const data = await loadAllData();
        const { q, classification, drug, company, dateFrom, dateTo, hasExpired, limit = 100, offset = 0 } = req.query;

        const filters = {
            classification,
            drug,
            company,
            dateFrom,
            dateTo,
            hasExpired: hasExpired === 'true' ? true : hasExpired === 'false' ? false : undefined
        };

        let results = searchPatents(data.patents, q, filters);

        // Pagination
        const total = results.length;
        results = results.slice(Number(offset), Number(offset) + Number(limit));

        res.json({
            total,
            limit: Number(limit),
            offset: Number(offset),
            results
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Patent detail
app.get('/api/patents/:id', async (req, res) => {
    try {
        const data = await loadAllData();
        const patent = data.patents.find(p =>
            p.id === req.params.id ||
            p.patent_number === req.params.id ||
            p.application_number === req.params.id
        );

        if (!patent) {
            return res.status(404).json({ error: 'Patent not found' });
        }

        // Find related drugs
        const relatedDrugs = data.drugs.filter(drug =>
            patent.drugs?.some(patentDrug =>
                drug.name?.toLowerCase() === patentDrug.toLowerCase()
            )
        );

        res.json({
            patent,
            relatedDrugs,
            relationships: data.relationships.filter(r =>
                r.patent_id === patent.id
            )
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Patents by drug
app.get('/api/patents/drug/:drugName', async (req, res) => {
    try {
        const data = await loadAllData();
        const drugName = decodeURIComponent(req.params.drugName);

        const patents = data.patents.filter(patent =>
            patent.drugs?.some(d =>
                d.toLowerCase().includes(drugName.toLowerCase())
            ) ||
            patent.compound_name?.toLowerCase().includes(drugName.toLowerCase())
        );

        res.json({
            drug: drugName,
            total: patents.length,
            patents
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Patents by company
app.get('/api/patents/company/:company', async (req, res) => {
    try {
        const data = await loadAllData();
        const company = decodeURIComponent(req.params.company);

        const patents = data.patents.filter(patent =>
            patent.grantees?.some(g =>
                g.toLowerCase().includes(company.toLowerCase())
            ) ||
            patent.original_applicants?.some(a =>
                a.toLowerCase().includes(company.toLowerCase())
            )
        );

        res.json({
            company,
            total: patents.length,
            patents
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Drug search
app.get('/api/drugs/search', async (req, res) => {
    try {
        const data = await loadAllData();
        const { q, phase, indication, company, target, launched, limit = 100, offset = 0 } = req.query;

        const filters = {
            phase,
            indication,
            company,
            target,
            launched: launched === 'true' ? true : launched === 'false' ? false : undefined
        };

        let results = searchDrugs(data.drugs, q, filters);

        // Pagination
        const total = results.length;
        results = results.slice(Number(offset), Number(offset) + Number(limit));

        res.json({
            total,
            limit: Number(limit),
            offset: Number(offset),
            results
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Drug detail
app.get('/api/drugs/:id', async (req, res) => {
    try {
        const data = await loadAllData();
        const drug = data.drugs.find(d =>
            d.id === req.params.id ||
            d.name?.toLowerCase() === req.params.id.toLowerCase()
        );

        if (!drug) {
            return res.status(404).json({ error: 'Drug not found' });
        }

        // Find related patents
        const relatedPatents = data.patents.filter(patent =>
            patent.drugs?.some(patentDrug =>
                patentDrug.toLowerCase() === drug.name?.toLowerCase()
            )
        );

        res.json({
            drug,
            relatedPatents,
            relationships: data.relationships.filter(r =>
                r.drug_id === drug.id
            )
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Analysis endpoints

// Patent landscape analysis
app.get('/api/analysis/patent-landscape', async (req, res) => {
    try {
        const data = await loadAllData();
        const { year, classification } = req.query;

        let patents = data.patents;

        // Filter by year if specified
        if (year) {
            patents = patents.filter(p =>
                p.application_date?.startsWith(year)
            );
        }

        // Filter by classification if specified
        if (classification) {
            patents = patents.filter(p =>
                p.classifications?.some(c =>
                    c.toLowerCase().includes(classification.toLowerCase())
                )
            );
        }

        // Analyze landscape
        const landscape = {
            totalPatents: patents.length,
            byYear: {},
            byClassification: {},
            byCompany: {},
            topDrugs: {},
            expiryAnalysis: {
                expired: 0,
                expiringThisYear: 0,
                expiringNext5Years: 0
            }
        };

        const now = new Date();
        const thisYear = now.getFullYear();

        patents.forEach(patent => {
            // By year
            const appYear = patent.application_date?.substring(0, 4);
            if (appYear) {
                landscape.byYear[appYear] = (landscape.byYear[appYear] || 0) + 1;
            }

            // By classification
            patent.classifications?.forEach(cls => {
                landscape.byClassification[cls] = (landscape.byClassification[cls] || 0) + 1;
            });

            // By company
            patent.grantees?.forEach(company => {
                landscape.byCompany[company] = (landscape.byCompany[company] || 0) + 1;
            });

            // By drug
            patent.drugs?.forEach(drug => {
                landscape.topDrugs[drug] = (landscape.topDrugs[drug] || 0) + 1;
            });

            // Expiry analysis
            if (patent.earliest_expiry_date) {
                const expiryDate = new Date(patent.earliest_expiry_date);
                if (expiryDate < now) {
                    landscape.expiryAnalysis.expired++;
                } else if (expiryDate.getFullYear() === thisYear) {
                    landscape.expiryAnalysis.expiringThisYear++;
                } else if (expiryDate.getFullYear() <= thisYear + 5) {
                    landscape.expiryAnalysis.expiringNext5Years++;
                }
            }
        });

        // Sort and limit top results
        landscape.byCompany = Object.fromEntries(
            Object.entries(landscape.byCompany)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 20)
        );

        landscape.topDrugs = Object.fromEntries(
            Object.entries(landscape.topDrugs)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 20)
        );

        res.json(landscape);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Drug pipeline analysis
app.get('/api/analysis/drug-pipeline', async (req, res) => {
    try {
        const data = await loadAllData();
        const { company, indication } = req.query;

        let drugs = data.drugs;

        // Filter by company if specified
        if (company) {
            drugs = drugs.filter(d =>
                d.active_companies?.some(c =>
                    c.toLowerCase().includes(company.toLowerCase())
                )
            );
        }

        // Filter by indication if specified
        if (indication) {
            drugs = drugs.filter(d =>
                d.active_indications?.some(i =>
                    i.toLowerCase().includes(indication.toLowerCase())
                )
            );
        }

        // Analyze pipeline
        const pipeline = {
            totalDrugs: drugs.length,
            byPhase: {},
            byIndication: {},
            byCompany: {},
            byTarget: {},
            recentLaunches: [],
            timeline: {}
        };

        const now = new Date();
        const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());

        drugs.forEach(drug => {
            // By phase
            const phase = drug.highest_phase || 'Unknown';
            pipeline.byPhase[phase] = (pipeline.byPhase[phase] || 0) + 1;

            // By indication
            drug.active_indications?.forEach(ind => {
                pipeline.byIndication[ind] = (pipeline.byIndication[ind] || 0) + 1;
            });

            // By company
            drug.active_companies?.forEach(comp => {
                pipeline.byCompany[comp] = (pipeline.byCompany[comp] || 0) + 1;
            });

            // By target
            drug.targets?.forEach(target => {
                pipeline.byTarget[target] = (pipeline.byTarget[target] || 0) + 1;
            });

            // Recent launches
            if (drug.first_launched_date) {
                const launchDate = new Date(drug.first_launched_date);
                if (launchDate > oneYearAgo) {
                    pipeline.recentLaunches.push({
                        name: drug.name,
                        date: drug.first_launched_date,
                        indication: drug.first_launched_indication,
                        country: drug.first_launched_country
                    });
                }

                // Timeline
                const year = launchDate.getFullYear();
                if (year >= 2020) {
                    pipeline.timeline[year] = (pipeline.timeline[year] || 0) + 1;
                }
            }
        });

        // Sort and limit results
        pipeline.byIndication = Object.fromEntries(
            Object.entries(pipeline.byIndication)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 30)
        );

        pipeline.byCompany = Object.fromEntries(
            Object.entries(pipeline.byCompany)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 30)
        );

        pipeline.byTarget = Object.fromEntries(
            Object.entries(pipeline.byTarget)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 30)
        );

        pipeline.recentLaunches.sort((a, b) => b.date.localeCompare(a.date));

        res.json(pipeline);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Competitive analysis
app.get('/api/analysis/competitive/:company', async (req, res) => {
    try {
        const data = await loadAllData();
        const company = decodeURIComponent(req.params.company);

        // Find company's patents
        const companyPatents = data.patents.filter(patent =>
            patent.grantees?.some(g =>
                g.toLowerCase().includes(company.toLowerCase())
            ) ||
            patent.original_applicants?.some(a =>
                a.toLowerCase().includes(company.toLowerCase())
            )
        );

        // Find company's drugs
        const companyDrugs = data.drugs.filter(drug =>
            drug.active_companies?.some(c =>
                c.toLowerCase().includes(company.toLowerCase())
            )
        );

        // Analyze competitive position
        const analysis = {
            company,
            overview: {
                totalPatents: companyPatents.length,
                totalDrugs: companyDrugs.length,
                launchedDrugs: companyDrugs.filter(d => d.highest_phase === 'Launched').length,
                pipelineDrugs: companyDrugs.filter(d => d.highest_phase !== 'Launched').length
            },
            patentPortfolio: {
                byYear: {},
                byClassification: {},
                keyDrugs: {},
                expiringPatents: []
            },
            drugPipeline: {
                byPhase: {},
                byIndication: {},
                keyTargets: {}
            },
            competitors: [],
            recentActivity: []
        };

        // Analyze patent portfolio
        const now = new Date();
        const twoYearsFromNow = new Date(now.getFullYear() + 2, now.getMonth(), now.getDate());

        companyPatents.forEach(patent => {
            // By year
            const year = patent.application_date?.substring(0, 4);
            if (year) {
                analysis.patentPortfolio.byYear[year] =
                    (analysis.patentPortfolio.byYear[year] || 0) + 1;
            }

            // By classification
            patent.classifications?.forEach(cls => {
                analysis.patentPortfolio.byClassification[cls] =
                    (analysis.patentPortfolio.byClassification[cls] || 0) + 1;
            });

            // Key drugs
            patent.drugs?.forEach(drug => {
                analysis.patentPortfolio.keyDrugs[drug] =
                    (analysis.patentPortfolio.keyDrugs[drug] || 0) + 1;
            });

            // Expiring patents
            if (patent.earliest_expiry_date) {
                const expiryDate = new Date(patent.earliest_expiry_date);
                if (expiryDate > now && expiryDate < twoYearsFromNow) {
                    analysis.patentPortfolio.expiringPatents.push({
                        patentNumber: patent.patent_number,
                        title: patent.title,
                        expiryDate: patent.earliest_expiry_date,
                        drugs: patent.drugs
                    });
                }
            }
        });

        // Analyze drug pipeline
        companyDrugs.forEach(drug => {
            // By phase
            const phase = drug.highest_phase || 'Unknown';
            analysis.drugPipeline.byPhase[phase] =
                (analysis.drugPipeline.byPhase[phase] || 0) + 1;

            // By indication
            drug.active_indications?.forEach(ind => {
                analysis.drugPipeline.byIndication[ind] =
                    (analysis.drugPipeline.byIndication[ind] || 0) + 1;
            });

            // Key targets
            drug.targets?.forEach(target => {
                analysis.drugPipeline.keyTargets[target] =
                    (analysis.drugPipeline.keyTargets[target] || 0) + 1;
            });
        });

        // Find competitors (companies with similar indications)
        const companyIndications = new Set();
        companyDrugs.forEach(drug => {
            drug.active_indications?.forEach(ind => companyIndications.add(ind));
        });

        const competitorScores = {};
        data.drugs.forEach(drug => {
            drug.active_companies?.forEach(comp => {
                if (!comp.toLowerCase().includes(company.toLowerCase())) {
                    drug.active_indications?.forEach(ind => {
                        if (companyIndications.has(ind)) {
                            competitorScores[comp] = (competitorScores[comp] || 0) + 1;
                        }
                    });
                }
            });
        });

        analysis.competitors = Object.entries(competitorScores)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .map(([name, score]) => ({ name, overlapScore: score }));

        // Sort and limit results
        analysis.patentPortfolio.keyDrugs = Object.fromEntries(
            Object.entries(analysis.patentPortfolio.keyDrugs)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
        );

        analysis.drugPipeline.byIndication = Object.fromEntries(
            Object.entries(analysis.drugPipeline.byIndication)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 15)
        );

        analysis.drugPipeline.keyTargets = Object.fromEntries(
            Object.entries(analysis.drugPipeline.keyTargets)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
        );

        res.json(analysis);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Expiry timeline
app.get('/api/analysis/expiry-timeline', async (req, res) => {
    try {
        const data = await loadAllData();
        const { startYear = new Date().getFullYear(), endYear = new Date().getFullYear() + 10 } = req.query;

        const timeline = {};

        // Initialize years
        for (let year = Number(startYear); year <= Number(endYear); year++) {
            timeline[year] = {
                count: 0,
                patents: []
            };
        }

        // Analyze patents
        data.patents.forEach(patent => {
            if (patent.earliest_expiry_date) {
                const expiryYear = Number(patent.earliest_expiry_date.substring(0, 4));
                if (expiryYear >= startYear && expiryYear <= endYear) {
                    timeline[expiryYear].count++;
                    timeline[expiryYear].patents.push({
                        patentNumber: patent.patent_number,
                        title: patent.title,
                        expiryDate: patent.earliest_expiry_date,
                        drugs: patent.drugs,
                        grantees: patent.grantees
                    });
                }
            }
        });

        // Sort patents within each year
        Object.values(timeline).forEach(yearData => {
            yearData.patents.sort((a, b) => a.expiryDate.localeCompare(b.expiryDate));
            // Limit to top 20 patents per year for response size
            yearData.patents = yearData.patents.slice(0, 20);
        });

        res.json({
            startYear: Number(startYear),
            endYear: Number(endYear),
            timeline
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Internal Server Error',
        message: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`\n${'='.repeat(80)}`);
    console.log(`PATENT DATABASE BACKEND SERVICE`);
    console.log(`${'='.repeat(80)}`);
    console.log(`Server running on port ${PORT}`);
    console.log(`API documentation: http://localhost:${PORT}/`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`${'='.repeat(80)}\n`);
});
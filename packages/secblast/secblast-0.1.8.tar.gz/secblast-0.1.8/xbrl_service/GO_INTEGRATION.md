# XBRL Processing Integration with Go Services

## Overview

The XBRL processor integrates with the existing filing pipeline at two points:

1. **RSS Real-Time Filings** - Process immediately but DON'T mark as processed
2. **Bulk Feed Ingestion** - Process after feed files and mark as processed

## Integration Points

### 1. RSS Real-Time Filings (Don't Mark)

**File:** `golang/services/DataService/FilingService/Fetch/file_based_rss_fetcher.go`

**Location:** After `IngestFilingBlocking()` call (~line 381)

```go
// ProcessFilingEntry processes a single filing entry from the feed
func (f *FileBasedRssFetcher) ProcessFilingEntry(item *gofeed.Item) error {
    // ... existing code ...

    // Ingest the filing in a separate goroutine
    go func(accessionNumber, cikNumber string) {
        atomic.AddInt64(&f.threadCount, 1)
        ingestorHandle := ingestor.NewIngestor()
        err := ingestorHandle.IngestFilingBlocking(accessionNumber, config_manager.CM.SBConfig.TableFilings, true)
        if err != nil {
            log.Printf("Error ingesting filing: %v", err)
            return
        }
        log.Printf("Ingested filing: %s", accessionNumber)

        // === ADD XBRL PROCESSING HERE ===
        // Process XBRL but DON'T mark as processed (real-time filings may not have all XBRL files)
        if err := TriggerXBRLProcessing(accessionNumber, false); err != nil {
            log.Printf("Warning: XBRL processing failed for %s: %v", accessionNumber, err)
            // Don't fail the filing ingestion for XBRL errors
        }
        // === END XBRL PROCESSING ===

        // ... rest of existing code (alerts, etc.) ...
    }(accNum, cik)

    return nil
}
```

### 2. Bulk Feed Processing (Mark as Processed)

**File:** `golang/services/DataService/FilingService/Fetch/run_all_pipeline.go`

**Location:** Add Step 7 after insider forms processing

```go
// RunAllPipeline executes the exact equivalent of run_all.sh
func RunAllPipeline() error {
    log.Println("====== STARTING run_all.sh PIPELINE ======")

    // Steps 1-6 remain unchanged...

    // Step 1: process_feed_files
    log.Println("Step 1/7: Processing feed files...")
    if err := processFeedFiles(); err != nil {
        return fmt.Errorf("process_feed_files failed: %v", err)
    }
    log.Println("Step 1/7: COMPLETED")

    // ... Steps 2-6 ...

    // === ADD NEW STEP 7 ===
    // Step 7: process_xbrl_batch
    log.Println("Step 7/7: Processing XBRL data...")
    if err := processXBRLBatch(); err != nil {
        // Log error but don't fail pipeline - XBRL is supplementary
        log.Printf("Warning: process_xbrl_batch had errors: %v", err)
    }
    log.Println("Step 7/7: COMPLETED")
    // === END NEW STEP ===

    log.Println("====== run_all.sh PIPELINE COMPLETED ======")
    return nil
}

// processXBRLBatch processes unprocessed XBRL filings
func processXBRLBatch() error {
    log.Println("Processing XBRL filings")

    // Call Python bulk processor with marking enabled
    return TriggerXBRLBatchProcessing(true)
}
```

### 3. XBRL Archive Processor (Mark as Processed)

**File:** `golang/cmd/xbrl_archive_processor/main.go`

**Location:** After `IngestFiling()` call (~line 331)

```go
// ProcessItem processes a single XBRL feed item
func (p *XbrlArchiveProcessor) ProcessItem(item *gofeed.Item) error {
    // ... existing code ...

    // Pass to ingestion only if not in dry run mode
    if !p.dryRun {
        ingestorHandle := ingestor.NewIngestor()
        err = ingestorHandle.IngestFiling(accNum, "rss_filings", true)
        if err != nil {
            log.Printf("Error ingesting filing: %v", err)
        }

        // === ADD XBRL PROCESSING HERE ===
        // Process XBRL and mark as processed (archive has complete XBRL data)
        if err := TriggerXBRLProcessing(accNum, true); err != nil {
            log.Printf("Warning: XBRL processing failed for %s: %v", accNum, err)
        }
        // === END XBRL PROCESSING ===

        // Send to alerts engine
        // ... existing code ...
    }

    return nil
}
```

## Helper Functions to Add

Create new file: `golang/services/XBRL/xbrl_trigger.go`

```go
package xbrl

import (
    "fmt"
    "log"
    "net/http"
    "os/exec"
    "time"
)

// TriggerXBRLProcessing processes a single filing's XBRL data
// markProcessed: if true, marks the filing as processed in sb_document_metadata
func TriggerXBRLProcessing(accessionNumber string, markProcessed bool) error {
    // Option 1: HTTP call to XBRL service
    url := fmt.Sprintf("http://sb_xbrl_service:8000/process/%s?mark=%v",
        accessionNumber, markProcessed)

    client := &http.Client{Timeout: 60 * time.Second}
    resp, err := client.Post(url, "application/json", nil)
    if err != nil {
        return fmt.Errorf("XBRL service call failed: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("XBRL service returned status %d", resp.StatusCode)
    }

    return nil
}

// TriggerXBRLBatchProcessing processes all unprocessed XBRL filings
func TriggerXBRLBatchProcessing(markProcessed bool) error {
    // Option 1: HTTP call to XBRL service batch endpoint
    url := fmt.Sprintf("http://sb_xbrl_service:8000/process/batch?mark=%v&limit=10000",
        markProcessed)

    client := &http.Client{Timeout: 30 * time.Minute}
    resp, err := client.Post(url, "application/json", nil)
    if err != nil {
        return fmt.Errorf("XBRL batch processing failed: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("XBRL batch service returned status %d", resp.StatusCode)
    }

    log.Println("XBRL batch processing completed successfully")
    return nil
}
```

## XBRL Service API Endpoints (To Add)

Add to `python_services/xbrl_service/src/main.py`:

```python
from fastapi import FastAPI, HTTPException, Query
from bulk_processor import process_single_filing, process_batch, get_unprocessed_filings
import psycopg2

app = FastAPI()

@app.post("/process/{accession_number}")
async def process_filing(accession_number: str, mark: bool = Query(default=True)):
    """Process a single filing's XBRL data."""
    acc, success, error, stats = process_single_filing(accession_number, mark)

    if success:
        return {"status": "success", "accession": acc, "stats": stats}
    else:
        raise HTTPException(status_code=500, detail=error)

@app.post("/process/batch")
async def process_filing_batch(mark: bool = Query(default=True), limit: int = Query(default=1000)):
    """Process unprocessed XBRL filings in batch."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        accessions = get_unprocessed_filings(conn, limit)
        if not accessions:
            return {"status": "success", "processed": 0, "message": "No filings to process"}

        results = process_batch(accessions, workers=4, mark_processed=mark)
        return {
            "status": "success",
            "processed": results['success'],
            "failed": results['failed'],
            "total_facts": results['total_facts']
        }
    finally:
        conn.close()
```

## Processing Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     RSS Real-Time Flow                          │
├─────────────────────────────────────────────────────────────────┤
│ SEC EDGAR Atom Feed                                             │
│     ↓                                                           │
│ file_based_rss_fetcher.ProcessFilingEntry()                     │
│     ↓                                                           │
│ Download documents                                              │
│     ↓                                                           │
│ IngestFilingBlocking() - index, split 8K/10K                    │
│     ↓                                                           │
│ TriggerXBRLProcessing(accNum, false)  ← DON'T MARK              │
│     ↓                                                           │
│ SendRSSFilingToAlertsEngine()                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Bulk Feed Flow                              │
├─────────────────────────────────────────────────────────────────┤
│ SEC EDGAR Daily Feed Files                                      │
│     ↓                                                           │
│ FetchSecFeed() → Download .nc files                             │
│     ↓                                                           │
│ RunAllPipeline()                                                │
│     │                                                           │
│     ├─ Step 1: processFeedFiles()                               │
│     ├─ Step 2: process8kBatch()                                 │
│     ├─ Step 3: bulkIndex()                                      │
│     ├─ Step 4: populateAutocompleteTable()                      │
│     ├─ Step 5: batchFilingSections()                            │
│     ├─ Step 6: processAllFormsParallel()                        │
│     └─ Step 7: processXBRLBatch()  ← MARK AS PROCESSED          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  XBRL Archive Flow                              │
├─────────────────────────────────────────────────────────────────┤
│ SEC EDGAR Monthly XBRL RSS Archive                              │
│     ↓                                                           │
│ XbrlArchiveProcessor.ProcessArchive()                           │
│     ↓                                                           │
│ ProcessItem() for each filing                                   │
│     ↓                                                           │
│ Download XBRL files                                             │
│     ↓                                                           │
│ IngestFiling()                                                  │
│     ↓                                                           │
│ TriggerXBRLProcessing(accNum, true)  ← MARK AS PROCESSED        │
└─────────────────────────────────────────────────────────────────┘
```

## Why Don't Mark for RSS?

RSS real-time filings may arrive before all XBRL documents are available on EDGAR. The SEC sometimes publishes filings in stages:

1. Primary HTML document appears first
2. XBRL instance documents appear later
3. Linkbase files (pre, cal, def, lab) may arrive even later

By NOT marking RSS filings as processed, the bulk pipeline will re-process them later when all documents are available.

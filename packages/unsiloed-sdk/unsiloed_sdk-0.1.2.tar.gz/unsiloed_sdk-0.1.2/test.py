from unsiloed_sdk import UnsiloedClient
import os
import json

client = UnsiloedClient(api_key="UNSILOED_API_KEY")
result = client.parse_and_wait(
    file="./test.pdf",
    merge_tables=True,
    use_high_resolution=True
)

print(f"Parsed {len(result.chunks)} chunks")
print(f"Status: {result.status}")
print(f"Job ID: {result.job_id}")
print(f"Total chunks: {result.total_chunks}")
print("\n" + "="*50)
print("RESULT DATA:")
print("="*50)

# Display all chunks
if result.chunks:
    for i, chunk in enumerate(result.chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Page number: {chunk.get('page_number', 'N/A')}")
        print(f"Segments: {len(chunk.get('segments', []))}")
        
        # Show segments
        for j, segment in enumerate(chunk.get('segments', []), 1):
            segment_type = segment.get('segment_type', 'unknown')
            content = segment.get('content', '')
            print(f"\n  Segment {j} ({segment_type}):")
            # Show first 200 characters of content
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"    {preview}")

# Optionally, save full result to a file
print("\n" + "="*50)
print("Saving full result to 'parse_result.json'...")
with open('parse_result.json', 'w') as f:
    # Convert result to dict for JSON serialization
    result_dict = {
        'job_id': result.job_id,
        'status': result.status,
        'file_name': result.file_name,
        'total_chunks': result.total_chunks,
        'chunks': result.chunks,
        'credit_used': result.credit_used,
        'quota_remaining': result.quota_remaining
    }
    json.dump(result_dict, f, indent=2)
print("✅ Full result saved to 'parse_result.json'")

client.close()
/**
 * Shared utilities for parsing and working with unified diff patches.
 */

export interface DiffLine {
  type: 'context' | 'added' | 'removed' | 'hunk'
  content: string
  oldLineNumber: number | null
  newLineNumber: number | null
}

export interface ParsedFile {
  lines: DiffLine[]
  oldPath: string | null
  newPath: string | null
  additions: number
  deletions: number
}

export interface ParsedDiff {
  files: ParsedFile[]
}

/**
 * Parse a unified diff patch into structured data for rendering.
 * Handles git diff format including new files (/dev/null), deleted files,
 * renames, and standard modifications.
 */
export function parseUnifiedDiff(patch: string): ParsedDiff {
  const lines = patch.split('\n')
  const files: ParsedFile[] = []
  
  let currentFile: ParsedFile | null = null
  let oldLineNum = 0
  let newLineNum = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // New file starts with 'diff --git'
    if (line.startsWith('diff --git')) {
      // Save previous file if exists
      if (currentFile) {
        files.push(currentFile)
      }
      // Extract paths from diff --git a/path b/path
      const match = line.match(/^diff --git a\/(.+?) b\/(.+)$/)
      currentFile = {
        lines: [],
        oldPath: match?.[1] || null,
        newPath: match?.[2] || null,
        additions: 0,
        deletions: 0,
      }
      continue
    }

    // Skip index and mode lines
    if (line.startsWith('index ') || line.startsWith('old mode') || line.startsWith('new mode') ||
        line.startsWith('new file mode') || line.startsWith('deleted file mode')) {
      continue
    }

    // Extract file paths (may override diff --git paths for renames/copies)
    if (line.startsWith('---')) {
      // Match both 'a/path' and '/dev/null' formats
      const match = line.match(/^---\s+(?:a\/)?(.+)$/)
      if (match && currentFile) {
        // Only update if not /dev/null (new file)
        if (match[1] !== '/dev/null') {
          currentFile.oldPath = match[1]
        } else {
          currentFile.oldPath = null
        }
      } else if (match && !currentFile) {
        // Handle patches without diff --git header
        currentFile = {
          lines: [],
          oldPath: match[1] !== '/dev/null' ? match[1] : null,
          newPath: null,
          additions: 0,
          deletions: 0,
        }
      }
      continue
    }
    if (line.startsWith('+++')) {
      // Match both 'b/path' and '/dev/null' formats
      const match = line.match(/^\+\+\+\s+(?:b\/)?(.+)$/)
      if (match && currentFile) {
        // Only update if not /dev/null (deleted file)
        if (match[1] !== '/dev/null') {
          currentFile.newPath = match[1]
        } else {
          currentFile.newPath = null
        }
      }
      continue
    }

    // Hunk header: @@ -oldStart,oldCount +newStart,newCount @@
    if (line.startsWith('@@')) {
      const match = line.match(/^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@/)
      if (match && currentFile) {
        oldLineNum = parseInt(match[1], 10)
        newLineNum = parseInt(match[3], 10)
        currentFile.lines.push({
          type: 'hunk',
          content: line,
          oldLineNumber: null,
          newLineNumber: null,
        })
      }
      continue
    }

    // Skip if no current file (shouldn't happen with valid diffs)
    if (!currentFile) continue

    // Diff lines
    if (line.startsWith(' ')) {
      // Context line (unchanged)
      currentFile.lines.push({
        type: 'context',
        content: line.substring(1),
        oldLineNumber: oldLineNum,
        newLineNumber: newLineNum,
      })
      oldLineNum++
      newLineNum++
    } else if (line.startsWith('-')) {
      // Removed line
      currentFile.lines.push({
        type: 'removed',
        content: line.substring(1),
        oldLineNumber: oldLineNum,
        newLineNumber: null,
      })
      currentFile.deletions++
      oldLineNum++
    } else if (line.startsWith('+')) {
      // Added line
      currentFile.lines.push({
        type: 'added',
        content: line.substring(1),
        oldLineNumber: null,
        newLineNumber: newLineNum,
      })
      currentFile.additions++
      newLineNum++
    }
    // Note: Empty lines without prefix are ignored (they're typically between files)
  }

  // Don't forget the last file
  if (currentFile) {
    files.push(currentFile)
  }

  return { files }
}

/**
 * Split a multi-file patch into individual file patches.
 * Returns an array of { path, content } objects where content is the
 * complete patch text for that file (suitable for passing to parseUnifiedDiff).
 */
export interface SplitPatchFile {
  path: string
  content: string
}

export function splitPatchByFile(patch: string): SplitPatchFile[] {
  const files: SplitPatchFile[] = []
  const lines = patch.split('\n')
  let currentFile: SplitPatchFile | null = null
  let seenPaths = new Set<string>()

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // Start of a new file in git diff format
    if (line.startsWith('diff --git')) {
      const match = line.match(/^diff --git a\/(.+?) b\/(.+)$/)
      if (match) {
        const path = match[2] // Use the 'b' path (destination)
        if (!seenPaths.has(path)) {
          if (currentFile) {
            files.push(currentFile)
          }
          seenPaths.add(path)
          currentFile = { path, content: line + '\n' }
        }
      }
      continue
    }
    
    if (line.startsWith('---') || line.startsWith('+++')) {
      // Match both a/path, b/path, and /dev/null formats
      const match = line.match(/^[+-]{3}\s+(?:(?:a|b)\/)?(.+)$/)
      if (match) {
        const path = match[1]
        const isDevNull = path === '/dev/null'
        
        if (!isDevNull && !seenPaths.has(path)) {
          // New file not yet seen (patch without diff --git header)
          if (currentFile) {
            files.push(currentFile)
          }
          seenPaths.add(path)
          currentFile = { path, content: line + '\n' }
        } else if (currentFile) {
          // Add to existing file (either same path or /dev/null)
          currentFile.content += line + '\n'
        } else if (isDevNull) {
          // /dev/null without a current file - start accumulating content
          // The actual file path will come from the +++ line
          currentFile = { path: 'pending', content: line + '\n' }
        }
      } else {
        if (currentFile) {
          currentFile.content += line + '\n'
        }
      }
    } else {
      if (currentFile) {
        currentFile.content += line + '\n'
      } else {
        // Lines before any file header - create a fallback
        if (line.startsWith('@@') || line.startsWith('+') || line.startsWith('-') || line.trim() === '') {
          if (!files.length) {
            files.push({ path: 'changes', content: line + '\n' })
          } else {
            files[files.length - 1].content += line + '\n'
          }
        }
      }
    }
  }

  if (currentFile) {
    // Fix up any 'pending' paths from /dev/null files
    if (currentFile.path === 'pending') {
      currentFile.path = 'changes'
    }
    files.push(currentFile)
  }

  if (files.length === 0 && patch.trim()) {
    files.push({ path: 'changes', content: patch })
  }

  return files
}

/**
 * Extract file paths from a patch without fully parsing it.
 * Useful for quickly listing which files are changed.
 */
export function getChangedFilePaths(patch: string): string[] {
  const parsed = parseUnifiedDiff(patch)
  return parsed.files.map(f => f.newPath || f.oldPath || 'unknown').filter(Boolean)
}

/**
 * Get summary statistics for a patch.
 */
export interface PatchStats {
  totalFiles: number
  totalAdditions: number
  totalDeletions: number
}

export function getPatchStats(patch: string): PatchStats {
  const parsed = parseUnifiedDiff(patch)
  return {
    totalFiles: parsed.files.length,
    totalAdditions: parsed.files.reduce((sum, f) => sum + f.additions, 0),
    totalDeletions: parsed.files.reduce((sum, f) => sum + f.deletions, 0),
  }
}




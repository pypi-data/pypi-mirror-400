# Redundant CLI Options Analysis

## Summary

The `list` command has a `--project` option that is redundant with the filter expression system. Users can already filter by project using `project:Work` syntax.

## Current Behavior

```bash
# Both of these do the same thing:
task-ng list --project Work
task-ng list project:Work
```

In `src/taskng/cli/commands/list.py:60-61`:
```python
if project:
    filters.append(Filter("project", "eq", project))
```

This creates a filter identical to what the filter parser would create from `project:Work`.

## Proposed Change

Remove the `--project` / `-p` option from the `list` command to:
1. **Simplify the CLI** - One way to do things instead of two
2. **Reduce cognitive load** - Users don't need to learn both methods
3. **Improve consistency** - Other filter-based commands (active, projects, tags, stats, calendar) don't have dedicated filter options
4. **Reduce maintenance** - Less code to maintain and test

## Migration Path Options

### Option 1: Hard removal (breaking change)
- Remove the option immediately
- Update documentation
- Add release note about breaking change

### Option 2: Deprecation period
- Keep the option but emit deprecation warning
- Update documentation to recommend filter syntax
- Remove in next major version

### Option 3: Keep but document as legacy
- Document `--project` as legacy/convenience option
- Recommend filter syntax in all examples
- Keep for backward compatibility

## Commands Analysis

### Commands using filter_args (consistent)
- `active` - No redundant options ✓
- `projects` - No redundant options ✓
- `tags` - No redundant options ✓
- `stats` - No redundant options ✓
- `calendar` - No redundant options ✓
- `board` - No redundant options ✓

### Commands with property options (correct usage)
- `add` - Options set task properties (not for filtering) ✓
- `modify` - Options set task properties (not for filtering) ✓

### Commands with redundant filtering options
- `list` - Has `--project` option ❌ (REDUNDANT)

## Recommendation

**Remove the `--project` option from `list` command** to align with other filtering commands and leverage the powerful filter expression system that already exists.

The filter syntax is:
- More powerful (supports hierarchical project filtering)
- More consistent (used across all commands)
- Better documented (part of core filtering documentation)
- More flexible (can combine with other filters naturally)

## Files to Change

If implementing removal:

1. **`src/taskng/cli/main.py:490-496`** - Remove project option from list_cmd
2. **`src/taskng/cli/commands/list.py:28-32`** - Remove project parameter
3. **`src/taskng/cli/commands/list.py:59-61`** - Remove project filter logic
4. **`docs/USER_GUIDE.md`** - Update all examples to use filter syntax
5. **Tests** - Update all tests using `--project` to use `project:` filter

## Example Migration

**Before:**
```bash
task-ng list --project Work
task-ng list -p Work
```

**After:**
```bash
task-ng list project:Work
```

**Multiple filters before:**
```bash
task-ng list --project Work +urgent
```

**Multiple filters after:**
```bash
task-ng list project:Work +urgent
```

The filter syntax is actually simpler and more consistent!

## Impact Assessment

### Pros of Removing
- ✅ Simplifies CLI interface
- ✅ Improves consistency across commands
- ✅ Reduces code complexity
- ✅ Easier to document (one way instead of two)
- ✅ Leverages existing powerful filter system
- ✅ Reduces maintenance burden

### Cons of Removing
- ⚠️ Breaking change for existing users
- ⚠️ Scripts using `--project` would break
- ⚠️ Shell completion for `-p` would be lost (though `project:` completion exists)

### Mitigation
- Add clear migration guide in release notes
- Consider deprecation period with warnings
- Update all documentation examples
- Provide migration script for common use cases

## Conclusion

The `--project` option on `list` is redundant and should be removed to improve CLI consistency. The filter expression system (`project:Work`) is more powerful, consistent, and better aligned with the rest of the application's design.

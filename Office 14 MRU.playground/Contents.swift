// MRU list generator for Mac Office 14 (2011)

import Foundation

func getMRUList(forApp: String) -> [String]? {
    guard let defaults = NSUserDefaults.standardUserDefaults().persistentDomainForName("com.microsoft.office") else {
        NSLog("Unable to find Office defaults")
        return nil
    }

    guard let mruList = defaults["14\\File MRU\\" + forApp ] as? [NSDictionary] else {
        NSLog("Unable to find recent documents for Office application \(forApp)")
        return nil
    }

    return mruList.flatMap { (mruItem: NSDictionary) in
        guard let mruFileAliasData = mruItem["File Alias"] as? NSData else {
            NSLog("Unable to extract file alias from MRU item \(mruItem)")
            return nil
        }
        do {
            let mruFileBookmarkData = CFURLCreateBookmarkDataFromAliasRecord(nil, mruFileAliasData).takeRetainedValue()
            let mruFileURL = try NSURL.init(byResolvingBookmarkData: mruFileBookmarkData, options: NSURLBookmarkResolutionOptions(), relativeToURL: nil, bookmarkDataIsStale: nil)
            return mruFileURL.path
        } catch let error as NSError {
            NSLog("Unable to resolve file alias for MRU item \(mruFileAliasData): \(error.localizedDescription)")
            return nil
        }
    }
}

if let mruList = getMRUList("MSWD") {
    print(NSString.init(data: try! NSJSONSerialization.dataWithJSONObject(mruList, options: NSJSONWritingOptions()), encoding: NSUTF8StringEncoding)!)
}

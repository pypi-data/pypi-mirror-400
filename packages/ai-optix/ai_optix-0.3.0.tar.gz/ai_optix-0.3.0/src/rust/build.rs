// SPDX-FileCopyrightText: 2025 ai-foundation-software
// SPDX-License-Identifier: Apache-2.0

fn main() {
    let dst = cmake::build("../../");

    // CMakeLists.txt installs to ".", so the lib is in the root of dst.
    println!("cargo:rustc-link-search=native={}", dst.display());
    println!("cargo:rustc-link-lib=static=kernels_cpu");

    // Link OpenMP if on Linux
    if std::env::consts::OS == "linux" {
        println!("cargo:rustc-link-lib=dylib=gomp");
        println!("cargo:rustc-link-lib=dylib=stdc++");
    }
}

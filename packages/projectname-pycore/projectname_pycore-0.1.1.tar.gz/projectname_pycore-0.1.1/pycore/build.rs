fn main() {
    let config = pyo3_build_config::get();

    pyo3_build_config::use_pyo3_cfgs();

    if !config.suppress_build_script_link_lines {
        if let Some(ref dir) = config.lib_dir {
            println!("cargo:rustc-link-search=native={dir}");
        }
        if let Some(ref name) = config.lib_name {
            println!("cargo:rustc-link-lib={name}");
        }
    }

    pyo3_build_config::add_extension_module_link_args();
}
